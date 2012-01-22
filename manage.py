#!/usr/bin/env env/bin/python
from flaskext.script import Manager
from app import app


manager = Manager(app)


@manager.command
def dumpconfig():
    """Dumps config"""

    print u'\n'.join(
        u'%s = %r' % item for item in sorted(app.config.items())
    )


if __name__ == '__main__':
    manager.run()

