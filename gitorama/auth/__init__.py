import urllib
import urlparse
import requests

from flask import (
    Blueprint,
    request,
    url_for, redirect, session,
    current_app,
)


OAUTH_AUTHORIZE_URL = 'https://github.com/login/oauth/authorize'
OAUTH_ACCESS_TOKEN_URL = 'https://github.com/login/oauth/access_token'
OAUTH_CLIENT_ID = '7cf20f0f8b99553252ee'
OAUTH_SECRET = '3331f02c56725f4981c2948f23a762e22229753c'

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['POST'])
def login():
    url = OAUTH_AUTHORIZE_URL + '?' + urllib.urlencode(dict(
        client_id=OAUTH_CLIENT_ID,
    ))
    return redirect(url)


@auth.route('/logout', methods=['POST'])
def logout():
    response = redirect(url_for('core.index'))
    session.pop('token', None)
    return response


@auth.route('/callback', methods=['GET'])
def auth_callback():
    code = request.args.get('code', '')
    data = requests.post(
        OAUTH_ACCESS_TOKEN_URL,
        urllib.urlencode(dict(
            client_id=OAUTH_CLIENT_ID,
            client_secret=OAUTH_SECRET,
            code=code,
        )),
        timeout=30,
    )
    result = dict(
        urlparse.parse_qsl(data.content)
    )
    current_app.logger.debug(result)

    token = result.get('access_token')

    response = redirect(url_for('core.index'))
    if token is not None:
        session['token'] = token

    return response

