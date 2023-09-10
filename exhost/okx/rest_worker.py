import os
import ccxt
from general.logger import setup_logger
from general.queue import RedisQueueHandler
from config.binancefuture_okx_arb import (LOG_DIR, TIMESTAMP, OKX_API_KEY, OKX_API_SECRET, OKX_PASSPHRASS,
                                          REDIS_HOST, REDIS_PORT, REDIS_QUEUE)

okx = ccxt.okex5(
    {
        'apiKey': OKX_API_KEY,
        'secret': OKX_API_SECRET,
        'password': OKX_PASSPHRASS,
        'options': {
            'defaultType': 'swap'
        },
    }
)


NAME = os.path.splitext(os.path.basename(__file__))[0]
logger = setup_logger(NAME, os.path.join(LOG_DIR, f"{TIMESTAMP}_{NAME}.log"))
logger.info(f"init {NAME}")

queue_handler = RedisQueueHandler(REDIS_HOST, REDIS_PORT, REDIS_QUEUE)

try:
    while True:
        message = queue_handler.dequeue()
        logger.info(f"Received message: {message}")

        if message['topic'] == 'create':
            if message['dry_run']:
                logger.info(f"Dry run order: {message=}")
            else:
                res = okx.create_order(message['symbol'], message['type'], message['side'], message['amount'], message['price'])
                logger.info(f"{res=}")
except KeyboardInterrupt:
    queue_handler.close()