import re
import anyjson
import requests

from functools import wraps
from urlparse import urljoin
from flask import current_app


def track_ratelimit(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        from .stats import stats

        response = func(*args, **kwargs)
        remaining = response.headers.get('x-ratelimit-remaining')
        if remaining is not None:
            stats.incr('github.api.calls.' + func.__name__)

            limit = response.headers.get('x-ratelimit-limit')
            if limit is not None:
                stats.save('github.rate-limit.current', limit)
                stats.save('github.rate-limit.remaining', remaining)
                stats.save('github.rate-limit.quota', float(remaining) / float(limit))
        return response
    return wrapper


get = track_ratelimit(requests.get)
post = track_ratelimit(requests.post)


class GitHubApiError(RuntimeError):
    def __init__(self, response):
        self.response = response
    def __unicode__(self):
        return u'GitHubApiError(status_code={0.status_code}, content={0.content})'.format(self.response)
    def __str__(self):
        return self.__unicode__().encode('utf-8')


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

            if not response.ok:
                raise GitHubApiError(response)

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

    def get_iter(self, resource, **kwargs):
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

            if not response.ok:
                raise GitHubApiError(response)

            data = anyjson.deserialize(response.content)
            for item in data:
                yield item

            if 'link' in response.headers:
                link = response.headers['link']
                match = re.search(r'.*<(.*)>; rel="next".*', link)
                if match is not None:
                    for item in get_while_next(match.group(1)):
                        yield item


        for item in get_while_next(
                urljoin(
                    current_app.config['GITHUB_API_URL'],
                    resource
                )
            ):
            yield item

