from redis import Redis
from rq import Queue
from rq_scheduler import Scheduler

from django.conf import settings


redis_conn = Redis(db=settings.RQ_REDIS_DB)
message_queue = Queue(name='message', connection=redis_conn)


