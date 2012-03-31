import time

from gitorama import core
from gitorama.core import net

def update():
    db = core.get_db()
    gh = net.GitHub()

    timestamp = int(time.time())

    db.followed.ensure_index('login', unique=True)

    for user in db.users.find({'gitorama.token': {'$exists': True}}):
        login = user['login']
        followed_doc = db.followed.find_one({'login': login})

        if followed_doc is None:
            followed_doc = {'login': login, 'users': []}
            # don't create events for the first run
            create_events = False
        else:
            create_events = True

        old_followed = set(followed_doc['users'])

        new_followed = gh.get('/users/{0}/following'.format(login))
        new_followed = set(f['login'] for f in new_followed)

        followed = new_followed - old_followed
        unfollowed = old_followed - new_followed

        if create_events:
            if followed:
                db.events.insert(
                    (
                        {'login': login, 'e': 'follow', 'who': who, 'ts': timestamp}
                        for who in followed
                    ),
                    manipulate = False,
                )

            if unfollowed:
                db.events.insert(
                    (
                        {'login': login, 'e': 'unfollow', 'who': who, 'ts': timestamp}
                        for who in unfollowed
                    ),
                    manipulate = False,
                )

        followed_doc['users'] = list(new_followed)
        db.followed.save(followed_doc, manipulate=False, safe=True)

