import os
import ccxt
import pika
import json

from general.logger import setup_logger
from general.queue import RedisQueueHandler
from config.binancefuture_okx_arb import (LOG_DIR, TIMESTAMP, BINANCE_API_KEY, BINANCE_SECRET_KEY,
                                          REDIS_HOST, REDIS_PORT, REDIS_QUEUE)

binance = ccxt.binance({
    'apiKey': BINANCE_API_KEY,
    'secret': BINANCE_SECRET_KEY,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future',
        }
})


NAME = os.path.splitext(os.path.basename(__file__))[0]
logger = setup_logger(NAME, os.path.join(LOG_DIR, f"{TIMESTAMP}_{NAME}.log"))
logger.info(f"init {NAME}")

queue_handler = RedisQueueHandler(REDIS_HOST, REDIS_PORT, REDIS_QUEUE)

try:
    while True:
        message = queue_handler.dequeue()
        logger.info(f"Received message: {message}")

        if message['topic'] == 'create':
            res = binance.create_order(message['symbol'], message['type'], message['side'], message['amount'], message['price'])
            logger.info(f"{res=}")
except KeyboardInterrupt:
    queue_handler.close()