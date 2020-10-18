import os
import redis

REDIS_URL = os.environ.get('REDIS_URL', 'redis://@localhost:6379/0')

conn = redis.from_url(REDIS_URL, decode_responses=True)

# hoge = conn.set('hoge', 3)
# # hoge = conn.get(None)
#
# print(hoge, type(hoge))
