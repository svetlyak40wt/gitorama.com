from gitorama import core

def migrate():
    db = core.get_db()
    db.raw_events.rename('received_events')

    for event in db.received_events.find():
        if 'gitorama' not in event:
            event['gitorama'] = {'login': 'svetlyak40wt'}
            db.received_events.save(event)

