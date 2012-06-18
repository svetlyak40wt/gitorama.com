#!/usr/bin/env env/bin/python
# -*- coding: utf-8 -*-
import times

from flask import g
from flaskext.script import Manager
from gitorama import core, app
from gitorama.features import forkfeed, relations

from rq import Queue, use_connection
from gitorama.core.jobs import update_user
from gitorama.core.pipeline import processor

manager = Manager(app)


@manager.command
def dump_config():
    """Dumps config"""

    print u'\n'.join(
        u'%s = %r' % item for item in sorted(app.config.items())
    )


@manager.command
def show_stats():
    """Dumps config"""

    for key in ['rate-limit']:
        print '{0}: {1}'.format(
            key,
            core.cache.get(key)
        )




@manager.command
def update_forkfeed():
    """Updates users fork feeds."""
    forkfeed.commands.update()


@manager.command
def push_processes(debug=False):
    processor.run(debug=debug)


if __name__ == '__main__':
    manager.run()

