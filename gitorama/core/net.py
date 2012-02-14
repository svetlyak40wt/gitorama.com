import re
import anyjson
import requests

from .cache import cache
from functools import wraps
from urlparse import urljoin
from flask import current_app


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


class GitHub(object):
    def __init__(self, token=None):
        self.token = token

    def get(self, resource, **kwargs):
        """
        '<https://api.github.com/user/repos?access_token=0e2bc18dab04cd09b02fa3f1b9f735896ac8569d&page=2>; rel="next", <https://api.github.com/user/repos?access_token=0e2bc18dab04cd09b02fa3f1b9f735896ac8569d&page=3>; rel="last"'
        """
        params = dict(
            per_page=100,
        )

        if self.token:
            params['access_token'] = self.token

        params.update(kwargs)

        def get_while_next(url):
            print 'GET:', url
            response = get(
                url,
                params=params,
                timeout=current_app.config['TIMEOUT'],
            )
            data = anyjson.deserialize(response.content)

            if 'link' in response.headers:
                link = response.headers['link']
                match = re.search(r'.*<(.*)>; rel="next".*', link)
                if match is not None:
                    data += get_while_next(match.group(1))

            return data

        return get_while_next(
            urljoin(
                current_app.config['GITHUB_API_URL'],
                resource
            )
        )

