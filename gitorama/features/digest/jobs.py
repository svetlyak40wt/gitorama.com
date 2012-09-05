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
    last_item = list(db.received_events.find({'gitorama.login': user['login']}).sort([('created_at', -1)])[:1])
    if last_item:
        last_item = last_item[0]['id'] # this is a GitHub's event id
    else:
        last_item = None

    gh = net.GitHub(token=user['gitorama']['token'])
    for event in gh.get_iter('/users/{0}/received_events'.format(user['login']), per_page=30):
        if event['id'] == last_item:
            # don't fetch more than needed
            # this item already saved
            break

        event['created_at'] = times.to_universal(event['created_at'])
        event['gitorama'] = {'login': user['login']}
        db.received_events.save(event)


def get_logins_to_build_digests_for(db):
    logins = set(u['_id'] for u in db.daily_digests.find({
        '$or': [
            {'update_at': {'$exists': False}},
            {'update_at': {'$lte': times.now()}},
        ],
    }, {'_id': True}))

    all_daily_digest_logins = set(u['_id'] for u in db.daily_digests.find({}, {'_id': True}))
    all_known_logins = set(u['login'] for u in db.users.find(
        {'gitorama.token': {'$exists': True}},
        {'login': True})
    )
    logins.update(all_known_logins - all_daily_digest_logins)
    return logins

@job(
    get_logins_to_build_digests_for
    #lambda db: (u['_id'] for u in db.daily_digests.find({
    #    '$or': [
    #        {'update_at': {'$exists': False}},
    #        {'update_at': {'$lte': times.now()}},
    #    ],
    #}, {'_id': True})),
)
def update_digest(login, collection_name='daily_digests', period=1):
    db = get_db()
    result = db.received_events.inline_map_reduce(
"""
    function() {
        var doc = {types: {}};
        var obj = {};

        function copy_actor(item) {
            return {
                login: item.actor.login,
                gravatar_id: item.actor.gravatar_id,
                url: item.actor.url
            }
        }

        if (this.type == 'WatchEvent') {
            obj.actor = copy_actor(this)
        } else if (this.type == 'ForkEvent') {
            obj.actor = copy_actor(this)
        } else if (this.type == 'GollumEvent') {
            obj.actor = copy_actor(this)
        } else if (this.type == 'PushEvent') {
            obj.actor = copy_actor(this)
            obj.commits = this.payload.commits
        } else if (this.type == 'PublicEvent') {
            obj.actor = copy_actor(this)
        } else if (this.type == 'IssuesEvent') {
            obj.actor = copy_actor(this)
            obj.action = this.payload.action
        } else {
            if (this.type != 'CreateEvent' && this.type != 'MemberEvent') {
                obj = 'unknown event'
            }
        }
        doc.types[this.type] = [obj];
        emit(this.repo.name, doc);
    }
""",
"""
    function (key, values) {
        var result = {types: {}};
        values.forEach(function(value) {
            for (var key in value.types) {
                if (result.types[key] === undefined) {
                    result.types[key] = [];
                }
                result.types[key] = result.types[key].concat(value.types[key])
            }
        });
        return result;
    }
""",
    query={
        'gitorama.login': login,
        'created_at': {'$gt': times.now() - datetime.timedelta(period)},
        'repo.name': {'$ne': '/'}
    },
    )

    repositories = []

    for item in result:
        name = item['_id']
        events = item['value']['types']
        score = 0
        good_events = {}
        for event_name, event_data in events.items():
            if event_data[0] == 'unknown event':
                print 'Unknown', event_name, 'in', name

            if event_name in ('ForkEvent', 'PushEvent', 'GollumEvent', 'WatchEvent', 'IssuesEvent'):
                good_events[event_name] = event_data
            score += len(event_data)

        if good_events:
            repositories.append(
                dict(name=name, events=good_events, score=score)
            )
    repositories.sort(key=lambda x: x['score'], reverse=True)

    digest = dict(repositories=repositories)
    digest['_id'] = login
    digest['update_at'] = times.now() + datetime.timedelta(1)

    db[collection_name].save(digest)

