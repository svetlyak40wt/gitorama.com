import times

from gitorama import core
from gitorama.core import net
from gitorama.core.pipeline import job

@job(
    lambda db: db.following.find()
)
def migrate_relations(following):
    db = core.get_db()
    followers = db.followers.find_one({'login': following['login']})

    db.relations.save(dict(
            login=following['login'],
            following=following['users'],
            followers=followers['users'],
            update_at=times.now(),
        ),
        safe=True
    )
    db.following.remove(following['_id'], safe=True)
    db.following.remove(followers['_id'], safe=True)


@job(
    lambda db: (u['login'] for u in db.relations.find({
        '$or': [
            {'update_at': {'$exists': False}},
            {'update_at': {'$lte': times.now()}},
        ],
    }, {'login': True})),
)
def update_relations(login):
    from gitorama import app
    db = core.get_db()
    gh = net.GitHub()
    now = times.now()

    db.relations.ensure_index('login', unique=True)
    doc = db.relations.find_one({'login': login})

    if 'following' not in doc and 'followers' not in doc:
        doc['following'] = []
        doc['followers'] = []
        # don't create events for the first run
        create_events = False
    else:
        create_events = True

    def process(handle, new_event, missing_event):
        """Process new users in following/followed lists.
        """
        old = set(doc[handle])

        new = gh.get('/users/{login}/{handle}'.format(**locals()))
        new = set(f['login'] for f in new)

        new_items = new - old
        absent_items = old - new

        if create_events:
            if new_items:
                db.events.insert(
                    (
                        {'login': login, 'e': new_event, 'who': who, 'date': now}
                        for who in new_items
                    ),
                    manipulate = False,
                )

            if absent_items:
                db.events.insert(
                    (
                        {'login': login, 'e': missing_event, 'who': who, 'date': now}
                        for who in absent_items
                    ),
                    manipulate = False,
                )

    process('following', 'follow', 'unfollow')
    process('followers', 'followed', 'unfollowed')
    doc['update_at'] = now + app.config['USER_UPDATE_INTERVAL']
    db.relations.save(doc, manipulate=False, safe=True)

