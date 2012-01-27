import requests

from .cache import cache
from functools import wraps


def track_ratelimit(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)
        remaining = response.headers.get('x-ratelimit-remaining')
        if remaining is not None:
            limit = response.headers.get('x-ratelimit-limit')
            if limit is not None:
                cache.set('rate-limit', float(remaining) / float(limit), 3600)
        return response
    return wrapper


get = track_ratelimit(requests.get)
post = track_ratelimit(requests.post)
