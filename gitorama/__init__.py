import os

from flask import Flask

from . import auth
from . import core
from .features import forkfeed

SECRET_KEY = 'K\xba\x8a\xe6&\xc9,\xa1\x0c\xe0\x97\xca\xb9\x9b\xd32\xe7\xbb\x1b\x1a\x91)QR'

app = Flask(__name__)
app.config.from_object(os.environ.get('SETTINGS', 'gitorama.settings.development'))

app.register_blueprint(core.bp)
app.register_blueprint(auth.bp, url_prefix='/auth')
app.register_blueprint(forkfeed.bp, url_prefix='/forkfeed')
app.secret_key = SECRET_KEY

core.cache.init_app(app)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)

