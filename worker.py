#!/usr/bin/env python

from flask import _request_ctx_stack

from rq import Worker, Queue
from rq.scripts.rqworker import setup_redis, parse_args
from rq.scripts import setup_default_arguments

from gitorama import app
from gitorama.flask_logbook import create_logger

class CustomWorker(Worker):
    def perform_job(self, job):
        with app.test_request_context():
            _request_ctx_stack.top.logbook_request_id = job.get_id()
            handlers = create_logger(app)
            with handlers:
                super(CustomWorker, self).perform_job(job)

args = parse_args()
setup_default_arguments(args, {})
setup_redis(args)
queue = Queue()
w = CustomWorker([queue])
w.work(burst=args.burst)
