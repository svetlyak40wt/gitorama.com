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
            user['gitorama'] = dict(
                registered_at=datetime.datetime.utcnow(),
                token=token,
            )
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
    conn = pymongo.Connection(
        host=[
            'localhost:32001',
            'localhost:32002',
            'localhost:32003',
        ],
        w=2
    )
    return conn.gitorama


