from time import time as get_timestamp


class Stats(object):
    # interval on which we are aggregating all stats
    interval = 60

    def __init__(self, db=None, time=get_timestamp):
        self._get_timestamp = time
        self._db = db

    @property
    def db(self):
        if callable(self._db):
            return self._db()
        return self_db

    def _get_key(self, name):
        timestamp = self._get_timestamp()
        key = 'stats:{0}:{1}'.format(
            name,
            int(timestamp / self.interval)
        )
        return key

    def save(self, name, value):
        key = self._get_key(name)
        self.db.lpush(key, value)
        self.db.expire(key, self.interval)

    def incr(self, name):
        self.save(name, 1)


    def reduce(self, name, func):
        if name.startswith('stats:'):
            key = name
        else:
            key = self._get_key(name)

        values = self.db.lrange(key, 0, -1)
        return func(values)

    def sum(self, name):
        return self.reduce(name, lambda values: sum(map(float, values)))

    def avg(self, name):
        def count_avg(values):
            l = len(values)
            if l > 0:
                return sum(map(float, values)) / l
            return 0
        return self.reduce(name, count_avg)

    def get_all_values(self):
        timestamp = self._get_timestamp()
        key_pattern = 'stats:{0}:{1}'.format(
            '*',
            int(timestamp / self.interval)
        )
        keys = self.db.keys(key_pattern)

        values = {}

        for key in keys:
            tail = key.split(':', 1)[1]
            name = tail.rsplit(':', 1)[0]

            try:
                aggregation_type, name = name.split(':', 1)
            except ValueError:
                aggregation_type = 'sum'

            value = getattr(self, aggregation_type)(key)
            values[name] = value

        return values


from . import get_redis
stats = Stats(db=get_redis)

