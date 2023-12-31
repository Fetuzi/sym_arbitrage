import os
import ccxt
import json
import traceback
from general.logger import setup_logger
from general.queue import RedisQueueHandler
from config.binancefuture_okx_arb import (LOG_DIR, TIMESTAMP, OKX,
                                          OKX_API_KEY, OKX_API_SECRET, OKX_PASSPHRASS,
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
logger = setup_logger(NAME, os.path.join(LOG_DIR, f"{NAME}_{OKX}_{TIMESTAMP}.log"))
logger.info(f"init {NAME}")

queue_handler = RedisQueueHandler(REDIS_HOST, REDIS_PORT, REDIS_QUEUE)

try:
    while True:
        try:
            message = queue_handler.dequeue()
            logger.info(f"Received message: {message}")
            if message is None:
                logger.warning("Received empty message")
                continue
            if message.get('dry_run'):
                logger.info(f"Dry run order: {message=}")
                continue

            if message.get('topic') == 'create':
                if message.get('type') == 'market':
                    res = okx.create_order(message['symbol'], 'market', message['side'], message['amount'])
                    logger.info(f"Order created: {res=}")
                elif message.get('type') == 'limit':
                    res = okx.create_order(message['symbol'], 'limit', message['side'], message['amount'], message['price'])
                    logger.info(f"Order created: {res=}")
                else:
                    logger.error(f"Unexpected market type: {message.get('type')}")
        except ccxt.NetworkError as e:
            logger.error(f"Network error: {e}\n{traceback.format_exc()}")
        except ccxt.ExchangeError as e:
            logger.error(f"Exchange error: {e}\n{traceback.format_exc()}")
        except ccxt.BaseError as e:
            logger.error(f"CCXT Base error: {e}\n{traceback.format_exc()}")
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}\n{traceback.format_exc()}")
        except KeyError as e:
            logger.error(f"Missing key in message: {e}\n{traceback.format_exc()}")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}\n{traceback.format_exc()}")
except KeyboardInterrupt:
    queue_handler.close()