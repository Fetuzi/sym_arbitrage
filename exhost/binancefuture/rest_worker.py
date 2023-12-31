import os
import traceback
from binance.um_futures import UMFutures
from binance.error import ClientError
from general.logger import setup_logger
from general.queue import RedisQueueHandler
from config.binancefuture_okx_arb import (LOG_DIR, TIMESTAMP, BINANCE,
                                          BINANCE_API_KEY, BINANCE_SECRET_KEY,
                                          REDIS_HOST, REDIS_PORT, REDIS_QUEUE)


um_futures_client = UMFutures(key=BINANCE_API_KEY, secret=BINANCE_SECRET_KEY)

NAME = os.path.splitext(os.path.basename(__file__))[0]
logger = setup_logger(NAME, os.path.join(LOG_DIR, f"{NAME}_{BINANCE}_{TIMESTAMP}.log"))
logger.info(f"init {NAME}")

queue_handler = RedisQueueHandler(REDIS_HOST, REDIS_PORT, REDIS_QUEUE)

try:
    while True:
        try:
            message = queue_handler.dequeue()
            logger.info(f"Received message: {message}")

            if message.get('dry_run'):
                logger.info(f"Dry run order: {message=}")
                continue

            if message.get('topic') == 'create':
                if message.get('type') == 'market':
                    res = um_futures_client.new_order(symbol=message['symbol'],
                                                      side=message["side"].upper(),
                                                      type='MARKET',
                                                      quantity=message["amount"]
                                                      )
                    logger.info(f"Order created: {res=}")
                elif message.get('type') == 'limit':
                    res = um_futures_client.new_order(symbol=message['symbol'],
                                                      side=message["side"].upper(),
                                                      type="MARKET",
                                                      quantity=message["amount"],
                                                      timeInForce="GTC",
                                                      price=message["price"]
                                                      )
                    logger.info(f"Order created: {res=}")
                else:
                    logger.error(f"Unexpected market type: {message.get('type')}")

        except ClientError as error:
            logger.error(
                "Found error. status: {}, error code: {}, error message: {}".format(
                    error.status_code, error.error_code, error.error_message
                )
            )
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}\n{traceback.format_exc()}")

except KeyboardInterrupt:
    queue_handler.close()
