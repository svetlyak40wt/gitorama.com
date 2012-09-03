from functools import wraps
from gitorama import core
from rq import Queue, use_connection


class Processor(object):
    def __init__(self):
        self.pipelines = []

    def register(self, list_getter, obj_processor):
        self.pipelines.append(
            (list_getter, obj_processor)
        )

    def run(self, debug=False):
        db = core.get_db()
        use_connection()
        q = Queue()

        for list_getter, obj_processor in self.pipelines:
            objects = list_getter(db)
            for obj in objects:
                if debug:
                    obj_processor(obj)
                else:
                    q.enqueue(obj_processor, obj)


def job(list_getter):
    def decorator(func):
        processor.register(list_getter, func)
        return func
    return decorator


processor = Processor()
