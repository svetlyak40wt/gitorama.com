import anyjson
import datetime
import pymongo

from urlparse import urljoin

from flask import (
    Blueprint, request, render_template,
    session, g, current_app,
    flash,
    url_for,
)

from . import net
from .cache import cache


bp = Blueprint('core', __name__)


@bp.route("/")
def index():
    return render_template('index.html')


@bp.before_app_request
def before_request():
    if request.path.startswith('/static/'):
        return

    g.db = get_db()

    token = session.get('token')
    if token is not None:
        user = g.db.users.find_one({'gitorama.token': token})

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

            existing_user = g.db.users.find_one({'login': user['login']})
            if existing_user is None:
                user['gitorama'] = dict(
                    registered_at=datetime.datetime.utcnow(),
                    token=token,
                )
            else:
                existing_user.setdefault('gitorama', {})
                existing_user['gitorama']['token'] = token
                user = existing_user

            g.db.users.save(user)

        request.user = user

        if user.get('gitorama', {}).get('unverified_email') and \
                not request.path.startswith('/auth/'):
            flash(
                'Please, verify email. If you don\'t received verification email, <a href="{url}">click here</a>.'.format(
                    url=url_for('auth.resend_validation_email'),
                ),
                'error'
            )


@bp.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.connection.close()


def get_db():
    mongo_hosts = current_app.config['MONGO_HOSTS'],
    if len(mongo_hosts) == 1:
        options = dict(host=mongo_hosts[0])
    else:
        options = dict(host=mongo_hosts, w=2)

    conn = pymongo.Connection(**options)
    return conn.gitorama


