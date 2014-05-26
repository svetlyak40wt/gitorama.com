import anyjson
import datetime
import pymongo
import logging
import redis

from urlparse import urljoin
from hashlib import md5
from itertools import chain
from collections import defaultdict

from flask import (
    Blueprint, request, render_template,
    session, g, current_app,
    flash,
    url_for,
    _app_ctx_stack,
)

from . import net
from .cache import cache


bp = Blueprint('core', __name__)


@bp.route("/")
def index():
    logger = logging.getLogger('core.index')

    db = get_db()

    if hasattr(request, 'user'):
        daily_digest = db.daily_digests.find_one({'_id': request.user['login']})

        if daily_digest is not None:
            def avatars(data):
                avatars = set()
                for item in data:
                    if 'actor' in item:
                        avatars.add((item['actor']['login'], item['actor']['gravatar_id']))
                    elif 'author' in item:
                        avatars.add((
                            item['author']['name'],
                            md5(item['author']['email'].strip().lower()).hexdigest()
                        ))

                avatars = [
                    u'<img class="avatar avatar__small" src="http://www.gravatar.com/avatar/{gravatar_id}?s=16&d=https://a248.e.akamai.net/assets.github.com%2Fimages%2Fgravatars%2Fgravatar-user-420.png" title="{name}"/>'.format(
                        gravatar_id=gravatar_id,
                        name=name,
                    )
                    for name, gravatar_id in avatars
                ]
                return u' '.join(avatars)

            def count_issues(data):
                counters = defaultdict(int)
                for item in data:
                    counters[item['action']] += 1
                return ', '.join(
                    '{0} {1}'.format(*item)
                    for item in counters.items()
                )

            events_map = {
                'ForkEvent': lambda data: u'forked {0} times by: {1}'.format(len(data), avatars(data)),
                'WatchEvent': lambda data: u'watched {0} times by: {1}'.format(len(data), avatars(data)),
                'PushEvent': lambda data: u'{0} commits by: {1}'.format(
                    sum(1 for i in chain(*(item['commits'] for item in data))),
                    avatars(chain(*(item['commits'] for item in data)))
                ),
                'GollumEvent': lambda data: u'wiki edited {0} times by: {1}'.format(len(data), avatars(data)),
                'IssuesEvent': lambda data: u'issues: ' + count_issues(data),
            }

            for rep in daily_digest['repositories']:
                rep['events'] = [
                    events_map.get(key, lambda data: None)(data) or ('Unknown event: ' + key)
                    for key, data in rep['events'].iteritems()
                ]
                if not current_app.debug:
                    rep['events'] = filter(lambda x: not x.startswith('Unknown'), rep['events'])
    else:
        daily_digest = None

    return render_template(
        'index.html',
        daily_digest=daily_digest,
    )

@bp.route("/blocks")
def blocks():
    return render_template('blocks.html')

@bp.before_app_request
def before_request():
    if request.path.startswith('/static/'):
        return

    request.app = current_app

    db = get_db()

    token = session.get('token')
    if token is not None:
        user = db.users.find_one({'gitorama.token': token})

        if user is None:
            # this is either a new user, nor he is already
            # exists in our database but with another token
            response = net.get(
                urljoin(
                    current_app.config['GITHUB_API_URL'],
                    '/user'
                ),
                params=dict(
                    access_token=token
                ),
                timeout=current_app.config['TIMEOUT'],
            )
            user = anyjson.deserialize(response.content)

            existing_user = db.users.find_one({'login': user['login']})
            if existing_user is None:
                user['gitorama'] = dict(
                    registered_at=datetime.datetime.utcnow(),
                    token=token,
                )
            else:
                existing_user.setdefault('gitorama', {})
                existing_user['gitorama']['token'] = token
                user = existing_user

            db.users.save(user)

        request.user = user

        if user.get('gitorama', {}).get('unverified_email') and \
                not request.path.startswith('/auth/'):
            flash(
                'Please, verify email. If you don\'t received verification email, <a href="{url}">click here</a>.'.format(
                    url=url_for('auth.resend_validation_email'),
                ),
                'error'
            )


def get_db():
    mongo_hosts = current_app.config['MONGO_HOSTS'],
    if len(mongo_hosts) == 1:
        options = dict(host=mongo_hosts[0])
    else:
        options = dict(host=mongo_hosts, w=2)

    conn = pymongo.Connection(**options)
    return conn.gitorama


def get_redis():
    ctx = _app_ctx_stack.top
    db = getattr(ctx, '_redis', None)
    if db is None:
        db = redis.StrictRedis(
            host=ctx.app.config['REDIS_HOST'],
            port=int(ctx.app.config['REDIS_PORT']),
        )
        ctx._redis = db
    return db

