import times
import datetime
import logging

from gitorama.core.pipeline import job
from gitorama.core import net, get_db


@job(
    lambda db: (u['login'] for u in db.users.find({
        'gitorama.token': {'$exists': True},
    }, {'login': True})),
)
def fetch_user_events(login):
    logger = logging.getLogger('events')
    logger.debug('fetching events for %s' % (login,))

    db = get_db()
    user = db.users.find_one({'login': login})

    # calculating time of last saved event
    last_item= list(db.received_events.find({'gitorama.login': user['login']}).sort([('created_at', -1)])[:1])
    if last_item:
        last_item = last_item[0]['created_at']
    else:
        last_item = times.now() - datetime.timedelta(30)

    gh = net.GitHub(token=user['gitorama']['token'])
    for event in gh.get_iter('/users/{0}/received_events'.format(user['login']), per_page=30):
        created_at = times.to_universal(event['created_at'])
        if created_at < last_item:
            # don't fetch more than needed
            # this item already saved
            break

        event['created_at'] = created_at
        event['gitorama'] = {'login': user['login']}
        db.received_events.save(event)

