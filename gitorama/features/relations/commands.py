import datetime

from gitorama import core
from gitorama.core import net

def update():
    db = core.get_db()
    gh = net.GitHub()

    today = datetime.datetime.utcnow()

    def track(handle, new_event, missing_event):
        collection = db[handle]
        collection.ensure_index('login', unique=True)

        for user in db.users.find({'gitorama.token': {'$exists': True}}):
            login = user['login']
            doc = collection.find_one({'login': login})

            if doc is None:
                doc = {'login': login, 'users': []}
                # don't create events for the first run
                create_events = False
            else:
                create_events = True

            old = set(doc['users'])

            new = gh.get('/users/{login}/{handle}'.format(**locals()))
            new = set(f['login'] for f in new)

            followed = new - old
            unfollowed = old - new

            if create_events:
                if followed:
                    db.events.insert(
                        (
                            {'login': login, 'e': new_event, 'who': who, 'date': today}
                            for who in followed
                        ),
                        manipulate = False,
                    )

                if unfollowed:
                    db.events.insert(
                        (
                            {'login': login, 'e': missing_event, 'who': who, 'date': today}
                            for who in unfollowed
                        ),
                        manipulate = False,
                    )

            doc['users'] = list(new)
            doc['updated'] = today
            collection.save(doc, manipulate=False, safe=True)

    track('following', 'follow', 'unfollow')
    track('followers', 'followed', 'unfollowed')

