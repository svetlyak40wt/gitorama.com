import urllib
import urlparse

from flask import (
    Blueprint,
    request,
    url_for, redirect, session,
    current_app,
)

from ..core import net


bp = Blueprint('auth', __name__)


@bp.route('/login', methods=['POST'])
def login():
    url = current_app.config['OAUTH_AUTHORIZE_URL'] + '?' + urllib.urlencode(dict(
        client_id=current_app.config['OAUTH_CLIENT_ID'],
    ))
    return redirect(url)


@bp.route('/logout', methods=['POST'])
def logout():
    response = redirect(url_for('core.index'))
    session.pop('token', None)
    return response


@bp.route('/callback', methods=['GET'])
def auth_callback():
    code = request.args.get('code', '')
    data = net.post(
        current_app.config['OAUTH_ACCESS_TOKEN_URL'],
        urllib.urlencode(dict(
            client_id=current_app.config['OAUTH_CLIENT_ID'],
            client_secret=current_app.config['OAUTH_SECRET'],
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

