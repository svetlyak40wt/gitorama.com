#!/usr/bin/env python

from rq import Worker, Queue
from rq.scripts.rqworker import setup_redis, parse_args

from gitorama import core

args = parse_args()
setup_redis(args)
w = Worker([Queue()])
w.work(burst=args.burst)
