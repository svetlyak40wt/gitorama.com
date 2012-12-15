import urllib
import urlparse
import hashlib
import random

from flask import (
    Blueprint,
    request,
    url_for, redirect, session,
    current_app,
    render_template,
    flash,
    g,
)
from flask.ext.mail import Message

from ..core import net
from .forms import RegistrationForm, EmailValidationForm


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

    user = g.db.users.find_one({'gitorama.token': token})
    if user and not user.get('gitorama', {}).get('email'):
        response = redirect(url_for('auth.registration'))
    else:
        response = redirect(url_for('core.index'))

    if token is not None:
        session['token'] = token

    return response


@bp.route('/registration', methods=('GET', 'POST'))
def registration():
    form = RegistrationForm(
        email=request.user.get('email'),
    )

    if form.validate_on_submit():
        request.user['gitorama']['unverified_email'] = form.email.data
        request.user['gitorama']['email_validation_token'] = hashlib.sha1(str(random.random())).hexdigest()
        request.user['gitorama']['timezone'] = form.timezone.data
        g.db.users.save(request.user)

        send_validation_email()

    return render_template('registration.html', form=form)


@bp.route('/validation/<token>', methods=('GET', 'POST'))
def validation(token):
    form = EmailValidationForm(token=token)
    user = g.db.users.find_one({'gitorama.email_validation_token': token})
    if not user:
        raise RuntimeError('invalid token')

    if form.validate_on_submit():
        user['gitorama']['email'] = user['gitorama']['unverified_email']
        del user['gitorama']['unverified_email']
        del user['gitorama']['email_validation_token']
        g.db.users.save(user)

        flash('Your account was activated. Thank you!')
        return redirect(url_for('core.index'))

    return render_template(
        'validation.html',
        form=form,
        email=request.user['gitorama']['unverified_email'],
    )

@bp.route('/resend-validation-email/', methods=('GET', 'POST'))
def resend_validation_email():
    email = request.user['gitorama']['unverified_email']
    token = request.user['gitorama']['email_validation_token']

    if request.method == 'POST':
        form = EmailValidationForm()
        if form.validate_on_submit():
            send_validation_email()
            return redirect(url_for('core.index'))
    else:
        form = EmailValidationForm(token=token)
    return render_template('resend-validation-email.html', email=email, form=form)


def send_validation_email():
    to_email = request.user['gitorama']['unverified_email']
    token = request.user['gitorama']['email_validation_token']
    msg = Message('Email Verification [Gitorama]', sender='info@' + request.host, recipients=[to_email])
    msg.html = render_template('email/validation.html', token=token)
    current_app.mail.send(msg)
    flash('We\'ve sent a verification email. Please, check your inbox.')

