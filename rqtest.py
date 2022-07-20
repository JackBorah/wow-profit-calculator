from rq import Queue
import redis
import os
from tet import count_words_at_url
import time

# Tell RQ what Redis connection to use
redis_conn = redis.from_url(os.environ.get("REDIS_URL"))
print(os.environ.get("REDIS_URL"))
q = Queue(connection=redis_conn)  # no args implies the default queue

# Delay execution of count_words_at_url('http://nvie.com')
job = q.enqueue(count_words_at_url, 'http://google.com')
print(job.result)   # => None

# Now, wait a while, until the worker is finished
time.sleep(2)
print(job.result)   # => 889
