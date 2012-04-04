#!/usr/bin/env env/bin/python
# -*- coding: utf-8 -*-
import datetime
import anyjson

from urlparse import urljoin

from flask import g
from flaskext.script import Manager
from gitorama import core, app
from gitorama.core import net
from gitorama.features import forkfeed, relations


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
    stats_to_save = (
        'followers', 'following', 'disk_usage', 'public_repos'
    )

    for user in g.db.users.find({'gitorama.token': {'$exists': True}}):
        gh = net.GitHub(token=user['gitorama']['token'])

        # update user's data
        new_user_data = gh.get('/user')
        user.update(new_user_data)
        g.db.users.save(user)

        # update users's repositories
        repositories = gh.get('/user/repos')

        for rep in repositories:
            rep_from_db = g.db.user_reps.find_one(
                {
                    'owner.login': rep['owner']['login'],
                    'name': rep['name']
                }
            ) or {}
            rep_from_db.update(rep)
            g.db.user_reps.save(rep_from_db)


        today = datetime.date.utcnow()
        today = datetime.datetime(today.year, today.month, today.day)
        key = dict(login=user['login'], date=today)
        stats = g.db.user_stats.find_one(key) or key

        stats.update(
            (key, value)
            for key, value in user.iteritems()
                if key in stats_to_save
        )
        g.db.user_stats.save(stats)


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

