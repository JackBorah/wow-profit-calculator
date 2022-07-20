from rq import Queue
from rqtest import conn
from tet import count_words_at_url

q = Queue(connection=conn)

result = q.enqueue(count_words_at_url, 'http://heroku.com')
