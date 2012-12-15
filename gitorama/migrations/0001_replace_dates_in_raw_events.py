import times
from gitorama import core

def migrate():
    db = core.get_db()
    for event in db.raw_events.find():
        if isinstance(event['created_at'], basestring):
            event['created_at'] = times.to_universal(event['created_at'])
            db.raw_events.save(event)
