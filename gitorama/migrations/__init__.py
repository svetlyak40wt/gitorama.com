# -*- coding: utf-8 -*-
import os
import importlib
import datetime

from gitorama import core, app


def is_applied(migration_name):
    db = core.get_db()
    migration = db.migrations.find_one({'name': migration_name})
    return migration is not None


def migrate():
    now = datetime.datetime.utcnow()

    for filename in os.listdir(os.path.dirname(__file__)):
        if not filename.startswith('__') and filename.endswith('.py'):
            migration_name = filename[:-3]
            if not is_applied(migration_name):
                print 'Applying "{0}" migration…'.format(migration_name)
                module = importlib.import_module('.' + migration_name, __name__)
                module.migrate()

                db = core.get_db()
                db.migrations.save(
                    dict(name=migration_name, migrated_at=now)
                )

