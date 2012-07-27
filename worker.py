#!/usr/bin/env python

from rq import Worker, Queue
from rq.scripts.rqworker import setup_redis, parse_args

from gitorama import core

args = parse_args()
setup_redis(args)
queue = Queue()
w = Worker([queue])
w.work(burst=args.burst)
