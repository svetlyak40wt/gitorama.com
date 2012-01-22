import anyjson
import datetime
import pymongo
import requests

from urlparse import urljoin

from flask import (
    Blueprint, request, render_template,
    session, g, current_app
)

bp = Blueprint('core', __name__)

@bp.route("/")
def index():
    return render_template('index.html')


@bp.before_request
def before_request():
    conn = pymongo.Connection('localhost', 27017)
    g.db = conn.gitorama

    token = session.get('token')
    if token is not None:
        user = g.db.users.find_one({'gitorama.token': token})

        if user is None:
            response = requests.get(
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
    g.db.connection.close()

