from redis import Redis
from rq import Queue
from rq_scheduler import Scheduler


redis_conn = Redis(db=0)
message_queue = Queue(name='message', connection=redis_conn)


