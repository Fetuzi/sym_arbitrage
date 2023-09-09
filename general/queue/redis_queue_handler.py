# RedisQueueHandler.py
import os
import json
import redis
from general.logger import setup_logger


NAME = os.path.splitext(os.path.basename(__file__))[0]
logger = setup_logger(NAME)
logger.info(f"init {NAME}")
class RedisQueueHandler:
    def __init__(self, host, port, queue_name):
        logger.info(f"Redis {host=}, {port=}")
        self.redis_conn = redis.Redis(host=host, port=port, db=0)
        self.queue_name = queue_name

    def enqueue(self, data):
        self.redis_conn.rpush(self.queue_name, json.dumps(data))

    def dequeue(self):
        _, msg = self.redis_conn.blpop(self.queue_name)
        return json.loads(msg)

    def close(self):
        del self.redis_conn
