import datetime
import os

DEBUG = False
PROPAGATE_EXCEPTIONS = False

GITHUB_API_URL = 'https://api.github.com'
TIMEOUT = 5

REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = os.environ.get('REDIS_PORT', 6379)

CACHE_TYPE = 'redis'
CACHE_KEY_PREFIX = 'cache:'
CACHE_REDIS_HOST = REDIS_HOST
CACHE_REDIS_PORT = REDIS_PORT

LOG_FILE = 'gitorama.log'

USER_UPDATE_INTERVAL = datetime.timedelta(0, 60 * 60)

MONGO_HOSTS = [
    'localhost:27017'
]

