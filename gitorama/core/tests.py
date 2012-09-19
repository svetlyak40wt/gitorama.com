from .. import app
from .stats import Stats, get_redis
from ..tests import drop_redis_keys
from nose.tools import eq_

_current_timestamp = 0

get_time = lambda: _current_timestamp

def set_time(value):
    global _current_timestamp
    _current_timestamp = value


def test_stats_sum():
    stats = Stats(get_time)
    with app.app_context():
        drop_redis_keys()

        values = (1, 1, 2, 3)

        for v in values:
            stats.save('some.value', v)

        eq_(stats.sum('some.value'), sum(values))


def test_stats_avg():
    stats = Stats(get_time)
    with app.app_context():
        drop_redis_keys()

        values = (1, 1, 2, 3)

        for v in values:
            stats.save('some.value', v)

        eq_(stats.avg('some.value'), sum(map(float, values)) / len(values))


def test_stats_periods():
    stats = Stats(get_time)
    with app.app_context():
        drop_redis_keys()

        stats.save('some.value', 1)
        stats.save('some.value', 2)

        set_time(stats.interval * 10)

        stats.save('some.value', 3)
        stats.save('some.value', 4)

        eq_(stats.sum('some.value'), 7)


def test_stats_on_absent_key():
    stats = Stats(get_time)
    with app.app_context():
        drop_redis_keys()
        eq_(stats.sum('some.absent.value'), 0)
        eq_(stats.avg('some.absent.value'), 0)


def test_stats_get_all_keys():
    stats = Stats(get_time)
    with app.app_context():
        drop_redis_keys()

        stats.save('blah.value', 1)
        stats.save('blah.value', 2)

        stats.save('avg:minor.value', 3)
        stats.save('avg:minor.value', 4)

        stats.save('sum:again.value', 5)
        stats.save('sum:again.value', 6)

        values = stats.get_all_values()

        eq_(
            {
                'blah.value': 3,
                'minor.value': (3.0 + 4.0) / 2,
                'again.value': 5 + 6,
            },
            values
        )
