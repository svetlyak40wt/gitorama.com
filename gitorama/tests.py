import os

from .core import get_redis
from . import app

def drop_redis_keys():
    db = get_redis()
    db.flushall()

def test_custom_redis_started_for_unittests():
    with app.app_context():
        assert 'REDIS_HOST' in os.environ
        assert 'REDIS_PORT' in os.environ

        assert os.environ['REDIS_HOST'] == 'localhost'
        assert os.environ['REDIS_PORT'] != '6379'

        db = get_redis()
        drop_redis_keys()
        opts = db.connection_pool.connection_kwargs

        assert os.environ['REDIS_HOST'] == opts['host']
        assert os.environ['REDIS_PORT'] == str(opts['port'])


def test_set_and_get_with_redis():
    with app.app_context():
        drop_redis_keys()

        db = get_redis()
        db.set('blah', 'minor')

        assert len(db.keys()) == 1
        assert db.get('blah') == 'minor'

