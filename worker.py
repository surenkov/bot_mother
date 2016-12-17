#!/usr/bin/env python3

import os
from sys import argv
from rq import Connection, Worker
from redis import Redis

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bot_mother.settings')
from django.conf import settings


with Connection():
    queues = argv[1:] or ['default']
    queue_conn = Redis(db=settings.RQ_REDIS_DB)

    w = Worker(queues, connection=queue_conn)
    w.work()
