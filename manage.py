#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import logging

# to activate jobs
import gitorama.features.digest.jobs

from flask import g
from flask.ext.script import Manager
from flask.ext.assets import ManageAssets
from gitorama import core, app
from gitorama.features import forkfeed, relations
from time import sleep, time
from socket import socket

from rq import Queue, use_connection
from gitorama.core.jobs import update_user
from gitorama.core.pipeline import processor

manager = Manager(app)
manager.add_command("assets", ManageAssets())


@manager.command
def dump_config():
    """Dumps config"""

    print u'\n'.join(
        u'%s = %r' % item for item in sorted(app.config.items())
    )


@manager.command
def show_stats():
    """Dumps config"""

    for key in ['rate-limit']:
        print '{0}: {1}'.format(
            key,
            core.cache.get(key)
        )

@manager.command
def send_stats_to_graphite():
    CARBON_SERVER = '127.0.0.1'
    CARBON_PORT = 2003

    sock = socket()

    try:
      sock.connect((CARBON_SERVER, CARBON_PORT))
    except:
      print 'Couldn\'t connect to %(server)s on port %(port)d, is carbon-agent.py running?' % { 'server':CARBON_SERVER, 'port':CARBON_PORT }
      return 1

    now = time()
    lines = []

    db = core.get_db()
    stats = {
        'rate-limit': lambda: core.cache.get(key) or 0,
        'num-users': lambda: db.users.find().count(),
    }

    for key, getter in stats.items():
        lines.append('gitorama.{key} {value} {now}'.format(
            key=key,
            value=getter(),
            now=now
        ))

        message = '\n'.join(lines) + '\n' #all lines must end in a newline
        sock.sendall(message)


@manager.command
def update_forkfeed():
    """Updates users fork feeds."""
    forkfeed.commands.update()


@manager.command
def push_processes(debug=False, periodically=None):
    if periodically is None:
        processor.run(debug=debug)
    else:
        while True:
            processor.run(debug=debug)
            sleep(int(periodically) * 60)



@manager.command
def test_logging():
    logger = logging.getLogger('blah')
    logger.info('Some info')
    logger.warning('Some warning')
    logger.error('Some error')
    try:
        print unknown_variable
    except Exception:
        logger.exception('Some exception')


@manager.command
def dbshell():
    db = core.get_db()
    result = db.connection.admin.command({'isMaster': 1})
    if 'primary' in result:
        host, port = result['primary'].split(':')
    else:
        host, port = 'localhost', 27017
    subprocess.call('mongo --host "{host}" --port "{port}" "{db.name}"'.format(**locals()), shell=True)


@manager.command
def is_all_mongos_are_up():
    db = core.get_db()
    result = db.connection.admin.command({'isMaster': 1})

    if 'setName' in result:
        result = db.connection.admin.command('replSetGetStatus')
        for member in result['members']:
            if member['state'] not in [1, 2, 7]:
                return 1
    return 0


@manager.command
def build_digest():
    from gitorama.features.digest.jobs import update_daily_digest
    update_daily_digest('svetlyak40wt')

@manager.command
def migrate():
    from gitorama import migrations
    migrations.migrate()


if __name__ == '__main__':
    manager.run()

