from redis import Redis
from rq_scheduler import Scheduler

redis_conn = Redis(db=0)
message_queue = Scheduler(queue_name='message', connection=redis_conn)


