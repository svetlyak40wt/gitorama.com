from gitorama import core

def migrate():
    db = core.get_db()

    if 'received_events' in db.collection_names():
        db.backup_events.insert(db.received_events.find(), safe=True)
        db.received_events.remove()

        for event in db.backup_events.find():
            event['id'] = event['_id']
            del event['_id']
            db.received_events.save(event)

        db.backup_events.drop()

