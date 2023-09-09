# RedisQueueHandler.py
import json
import redis

class RedisQueueHandler:
    def __init__(self, host, port, queue_name):
        self.redis_conn = redis.Redis(host=host, port=port, db=0)
        self.queue_name = queue_name

    def enqueue(self, data):
        self.redis_conn.rpush(self.queue_name, json.dumps(data))

    def dequeue(self):
        _, msg = self.redis_conn.blpop(self.queue_name)
        return json.loads(msg)

    def close(self):
        del self.redis_conn
