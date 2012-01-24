from flask import Flask
from . import auth
from . import core

SECRET_KEY = 'K\xba\x8a\xe6&\xc9,\xa1\x0c\xe0\x97\xca\xb9\x9b\xd32\xe7\xbb\x1b\x1a\x91)QR'

app = Flask(__name__)
app.config.from_object('gitorama.settings.development')

app.register_blueprint(core.bp)
app.register_blueprint(auth.bp, url_prefix='/auth')
app.secret_key = SECRET_KEY

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)

