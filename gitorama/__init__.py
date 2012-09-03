import os
#import logging

from flask import Flask
from flask.ext.assets import Environment, Bundle
from flask.ext.mail import Mail

from . import auth
from . import core
from .features import forkfeed, userprofile, relations
from .flask_logbook import Logbook

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
logbook = Logbook(app)

try:
    from flask.ext.debugtoolbar import DebugToolbarExtension
    toolbar = DebugToolbarExtension(app)
except ImportError:
    pass

assets = Environment(app)
assets.cache = False
assets.manifest = 'file:'

import envoy
def stylus(_in, out, **kwargs):
    result = envoy.run('stylus --include /home/vagrant/osbench/workbench/stylus-nib/0.8.1/node_modules/nib/lib', data=_in.read())
    out.write(result.std_out)

css = Bundle('less/site.less', filters=['less'], output='css/site.css')
css_stylus = Bundle('stylus/site.styl', filters=[stylus], output='css/stylus.css')

assets.register('css_all', css)
assets.register('css_stylus', css_stylus)

js = Bundle('coffee/site.coffee', filters=['coffeescript'], output='js/site.js')
assets.register('js_all', js)

#logging.basicConfig(filename=app.config['LOG_FILE'], level=logging.DEBUG)

if app.config.get('ENVIRONMENT') == 'production':
    pass
    #mail_handler = logging.handlers.SMTPHandler(
    #    ('mailtrap.io', '2525'),
    #    'server-error@gitorama.com',
    #    ['svetlyak.40wt@gmail.com'],
    #    'gitorama.com ERROR',
    #    credentials=('dev-gitorama-com', '35164686f8911b01'),
    #)
else:
    pass
    #mail_handler = logging.handlers.SMTPHandler(
    #    ('localhost', '2525'),
    #    'server-error@gitorama.com',
    #    ['svetlyak.40wt@gmail.com'],
    #    'gitorama.com ERROR',
    #)

#mail_handler.setLevel(logging.ERROR)
#logging.getLogger().addHandler(mail_handler)

