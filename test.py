#!/usr/bin/env python

import nose
import os
import logging
import shutil
import tempfile
import random
import re
import envoy
import signal

from nose.plugins import Plugin


class TestRedis(Plugin):
    name = 'redis'

    def options(self, parser, env=os.environ):
        super(TestRedis, self).options(parser, env=env)
        self.base_config = '/etc/redis/redis.conf'
        self.port = random.randint(1024, 65535)

    def configure(self, options, conf):
        super(TestRedis, self).configure(options, conf)
        if not self.enabled:
            return

        self.logger = logging.getLogger('nose.plugins.' + self.name)

        self.root = tempfile.mkdtemp()
        self.pid_file = os.path.join(self.root, 'redis.pid')
        self.log_file = os.path.join(self.root, 'redis.log')
        self.config_file = os.path.join(self.root, 'redis.conf')

        with open(self.base_config) as base_config:
            with open(self.config_file, 'w') as config_file:
                config = base_config.read()

                values = dict(
                    loglevel='warning',
                    logfile=self.log_file,
                    pidfile=self.pid_file,
                    port=self.port,
                    dir=self.root,
                )

                def replacer(match):
                    key = match.group(1)
                    return '{0} {1}'.format(key, values[key])

                for key in values:
                    config = re.sub(r'(?m)^({0})\W+(.*)$'.format(key), replacer, config)

                config_file.write(config)

        result = envoy.run('redis-server ' + self.config_file)
        if result.status_code != 0:
            raise RuntimeError('Can\'t start Redis: ' + result.std_err)

        os.environ['REDIS_HOST'] = 'localhost'
        os.environ['REDIS_PORT'] = str(self.port)


    def finalize(self, result):
        with open(self.pid_file) as pid_file:
            pid = int(pid_file.readline().strip())

        self.logger.info('Killing pid {0}'.format(pid))
        os.kill(pid, signal.SIGINT)

        shutil.rmtree(self.root)

if __name__ == '__main__':
    nose.main(addplugins=[TestRedis()])

