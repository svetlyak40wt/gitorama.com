from __future__ import absolute_import

import collectd
import time
import random
import redis
import logging
from functools import wraps

from gitorama.core.stats import Stats


class Plugin(object):
    name = None

    def __init__(self):
        assert self.name

        for name in dir(self):
            if name.startswith('on_'):
                callback_name = name[3:]
                try:
                    register = getattr(collectd, 'register_' + callback_name)
                except AttributeError:
                    raise RuntimeError('Wrong callback name: \'{0}\'.'.format(callback_name))

                register(getattr(self, name))

        def wrap_log(func):
            @wraps(func)
            def wrapper(msg):
                return func('{0} plugin: {1}'.format(self.name, msg))
            return wrapper

        for name in 'error', 'warning', 'info', 'debug':
            setattr(self, name, wrap_log(getattr(collectd, name)))

    def on_config(self, conf):
        for node in conf.children:
            if len(node.values) == 1:
                value = node.values
            else:
                value = node.values[0]

            setattr(self, node.key.lower(), value)

    def on_flush(self, timeout, identifier):
        pass

    def on_init(self):
        pass

    def on_log(self, severity, message):
        pass

    def on_notification(self, notification):
        pass

    def on_read(self):
        pass

    def on_shutdown(self):
        pass

    def on_write(self, values):
        pass

    def dispatch_value(self, key, value, type):
        self.debug('Sending value: {0}={1}'.format(key, value))

        val = collectd.Values(plugin=self.name)
        val.type = type
        val.type_instance = key
        val.values = [value]
        val.dispatch()


class GitoramaStats(Plugin):
    name = 'gitorama'
    host = 'localhost'
    port = 6379

    def __init__(self):
        super(GitoramaStats, self).__init__()
        self._db = None
        self.stats = Stats(self.get_redis)

    def get_redis(self):
        if self._db is None:
            self._db = redis.StrictRedis(
                host=self.host,
                port=self.port,
            )
        return self._db

    def on_read(self):
        values = self.stats.get_all_values()
        for key, value in values.items():
            self.dispatch_value(key, value, 'gauge')


plugin = GitoramaStats()

