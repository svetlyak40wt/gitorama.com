import time

from gitorama import core
from gitorama.core import net


def create_fork_watches():
    db = core.get_db()

    for user in db.users.find():
        num_fork_watches = db.fork_warches.find(
            {'login': user['login']}
        ).count()

        if num_fork_watches == 0:
            for rep in db.user_reps.find({'owner.login': user['login']}):
                db.fork_watches.save(dict(
                    login=user['login'],
                    name=rep['name'],
                ))


def update_reps_data():
    db = core.get_db()
    gh = net.GitHub()

    timestamp = int(time.time())

    query = {
        '$or': [
            {'gitorama.updated_at': {'$exists': False}},
            {'gitorama.updated_at': {'$lt': timestamp - 24 * 3600}},
        ]
    }

    for rep in db.user_reps.find(query):
        # update rep's data
        new_rep_data = gh.get('/repos/{0[owner][login]}/{0[name]}'.format(rep))
        rep.update(new_rep_data)
        rep.setdefault('gitorama', {})
        rep['gitorama']['updated_at'] = timestamp
        db.user_reps.save(rep)

    # TODO: add update of the new user's repositories


def cluster_reps_into_networks():
    db = core.get_db()
    gh = net.GitHub()

    query = {'gitorama.net_id': {'$exists': False}}

    rep = db.user_reps.find(query).limit(1)
    while rep:
        forks = gh.get('/repos/{0[owner][login]}/{0[name]}/forks'.format(rep))
        import pdb;pdb.set_trace()


def update():
    """Updates users fork feeds."""

    #create_fork_watches()
    cluster_reps_into_networks()
