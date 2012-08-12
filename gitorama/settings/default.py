import datetime

DEBUG = False
PROPAGATE_EXCEPTIONS = False

GITHUB_API_URL = 'https://api.github.com'
TIMEOUT = 5

CACHE_TYPE = 'redis'
CACHE_KEY_PREFIX = 'grama:'

LOG_FILE = 'gitorama.log'

USER_UPDATE_INTERVAL = datetime.timedelta(0, 60 * 60)

MONGO_HOSTS = [
    'localhost:27017'
]

