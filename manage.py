#!/usr/bin/env env/bin/python
import datetime
import anyjson

from urlparse import urljoin

from flask import g
from flaskext.script import Manager
from gitorama import core, app
from gitorama.core import net


manager = Manager(app)


@manager.command
def dump_config():
    """Dumps config"""

    print u'\n'.join(
        u'%s = %r' % item for item in sorted(app.config.items())
    )


@manager.command
def update_users():
    """Updates users profiles and collects stats."""
    g.db = core.get_db()
    stats_to_save = (
        'followers', 'following', 'disk_usage', 'public_repos'
    )

    for user in g.db.users.find({'gitorama.token': {'$exists': True}}):

        # update user's dict
        response = net.get(
            urljoin(
                app.config['GITHUB_API_URL'],
                '/user'
            ),
            params=dict(
                access_token=user['gitorama']['token']
            ),
            timeout=app.config['TIMEOUT'],
        )
        new_data = anyjson.deserialize(response.content)

        user.update(new_data)
        g.db.users.save(user)

        # save some stats
        today = datetime.date.today()
        today = datetime.datetime(today.year, today.month, today.day)
        key = dict(login=user['login'], date=today)
        stats = g.db.user_stats.find_one(key) or key

        stats.update(
            (key, value)
            for key, value in user.iteritems()
                if key in stats_to_save
        )
        g.db.user_stats.save(stats)


if __name__ == '__main__':
    manager.run()

