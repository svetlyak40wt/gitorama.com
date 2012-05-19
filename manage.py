#!/usr/bin/env env/bin/python
# -*- coding: utf-8 -*-
import times

from flask import g
from flaskext.script import Manager
from gitorama import core, app
from gitorama.features import forkfeed, relations

from rq import Queue, use_connection
from gitorama.core.jobs import update_user

manager = Manager(app)


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
def update_users():
    """Updates users profiles and collects stats."""
    g.db = core.get_db()
    use_connection()
    q = Queue()
    now = times.now()

    users_to_update = g.db.users.find({
        'gitorama.token': {'$exists': True},
        '$or': [
            {'gitorama.update_at': {'$exists': False}},
            {'gitorama.update_at': {'$lte': now}},
        ],
    })

    for user in users_to_update:
        q.enqueue(update_user, user['login'])


@manager.command
def update_forkfeed():
    """Updates users fork feeds."""
    forkfeed.commands.update()


@manager.command
def update_relations_stats():
    """Checks for new followers and who you followed too."""
    relations.commands.update()


if __name__ == '__main__':
    manager.run()

