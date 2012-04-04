import anyjson
import datetime
import pymongo

from urlparse import urljoin

from flask import (
    Blueprint, request, render_template,
    session, g, current_app
)

from . import net
from .cache import cache


bp = Blueprint('core', __name__)


@bp.route("/")
def index():
    return render_template('index.html')


@bp.before_app_request
def before_request():
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


@bp.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.connection.close()


def get_db():
    conn = pymongo.Connection('localhost', 27017)
    return conn.gitorama


