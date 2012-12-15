import times
import logging
import datetime

from flask import g
from gitorama import core, app
from gitorama.core import net
from gitorama.core.pipeline import job


@job(
    lambda db: (u['login'] for u in db.users.find({
        'gitorama.token': {'$exists': True},
        '$or': [
            {'gitorama.update_at': {'$exists': False}},
            {'gitorama.update_at': {'$lte': times.now()}},
        ],
    }, {'login': True})),
)
def update_user(login):
    g.db = core.get_db()
    now = times.now()

    stats_to_save = (
        'followers', 'following', 'disk_usage', 'public_repos'
    )

    user = g.db.users.find_one({'login': login})

    gh = net.GitHub(token=user['gitorama']['token'])

    # update user's data
    new_user_data = gh.get('/user')
    user.update(new_user_data)
    user['gitorama']['update_at'] = now + app.config['USER_UPDATE_INTERVAL']
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


    today = datetime.datetime(now.year, now.month, now.day)
    key = dict(login=user['login'], date=today)
    stats = g.db.user_stats.find_one(key) or key

    stats.update(
        (key, value)
        for key, value in user.iteritems()
            if key in stats_to_save
    )
    g.db.user_stats.save(stats)


#@job(lambda db: [1])
#def log_error(number):
#    logger = logging.getLogger('blah')
#    logger.debug('Some debug message')
#    logger.info('Some info message')
#    logger.warning('Some warning message')
#    raise RuntimeError('Some error from job')
#
