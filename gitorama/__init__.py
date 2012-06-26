import os
import logging

from flask import Flask
from flaskext.assets import Environment, Bundle
from flaskext.mail import Mail

from . import auth
from . import core
from .features import forkfeed, userprofile, relations

SECRET_KEY = 'K\xba\x8a\xe6&\xc9,\xa1\x0c\xe0\x97\xca\xb9\x9b\xd32\xe7\xbb\x1b\x1a\x91)QR'

app = Flask(__name__)
app.config.from_object(os.environ.get('SETTINGS', 'gitorama.settings.development'))

app.register_blueprint(core.bp)
app.register_blueprint(auth.bp, url_prefix='/auth')
app.register_blueprint(forkfeed.views.bp, url_prefix='/forkfeed')
app.register_blueprint(relations.views.bp, url_prefix='/relations')
app.register_blueprint(userprofile.views.bp)
app.secret_key = SECRET_KEY

app.mail = Mail(app)
core.cache.init_app(app)

assets = Environment(app)
css = Bundle('less/site.less', filters=['less'], output='css/site.css')
assets.register('css_all', css)
js = Bundle('coffee/site.coffee', filters=['coffeescript'], output='js/site.js')
assets.register('js_all', js)

logging.basicConfig(filename=app.config['LOG_FILE'], level=logging.DEBUG)

if not app.debug:
    mail_handler = logging.handlers.SMTPHandler(
        #('mailtrap.io', '2525'),
        ('localhost', '25'),
        'server-error@gitorama.com',
        ['svetlyak.40wt@gmail.com'],
        'gitorama.com ERROR',
        #credentials=('dev-gitorama-com', '35164686f8911b01'),
    )
    #mail_handler = logging.handlers.SMTPHandler(
    #    ('mailtrap.io', '2525'),
    #    'server-error@gitorama.com',
    #    ['svetlyak.40wt@gmail.com'],
    #    'gitorama.com ERROR',
    #    credentials=('dev-gitorama-com', '35164686f8911b01'),
    #)
    mail_handler.setLevel(logging.ERROR)
    logging.getLogger().addHandler(mail_handler)

