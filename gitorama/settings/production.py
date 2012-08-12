from .default import *

ENVIRONMENT = 'production'

OAUTH_AUTHORIZE_URL = 'https://github.com/login/oauth/authorize'
OAUTH_ACCESS_TOKEN_URL = 'https://github.com/login/oauth/access_token'
OAUTH_CLIENT_ID = 'b1c68251f690bb495097'
OAUTH_SECRET = '39a56d4721d884a200ba72362468e44be0a5167c'

LOG_FILE = '/home/art/log/backend/gitorama.log'

MONGO_HOSTS = [
    'localhost:32001',
    'localhost:32002',
    'localhost:32003',
]
