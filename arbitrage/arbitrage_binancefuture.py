import os
import time
import traceback
import json
import redis

from general.logger import setup_logger
from config.binancefuture_okx_arb import TIMESTAMP, LOG_DIR, RECORDING_COIN, REDIS_HOST, REDIS_PORT, REDIS_PUBSUB, BINANCE, OKX

NAME = os.path.splitext(os.path.basename(__file__))[0]
logger = setup_logger(NAME, os.path.join(LOG_DIR, f"{TIMESTAMP}_{NAME}_{RECORDING_COIN}.log"))
logger.info(f"init {NAME}")


class SymmetricArbitrage:
    TRANS_STRATEGY = 1.001801531302 * 1.0002

    def __init__(self):
        # status
        self.time = int(time.time() * 1000)
        self.contract = {BINANCE: 0, OKX: 0}

        # Redis
        self.redis_conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
        self.redis_channel = REDIS_PUBSUB

    def run(self):
        pubsub = None
        try:
            pubsub = self.redis_conn.pubsub()
            pubsub.subscribe(self.redis_channel)

            # Skip the first message (the subscription confirmation)
            confirmation = next(pubsub.listen())
            logger.info(f'Confirmation: {confirmation}')

            for message in pubsub.listen():
                data = json.loads(message['data'].decode('utf-8'))
                logger.info(f'{data=}')

        except Exception as e:
            logger.info(f'Error occurred: {traceback.format_exc()}')
        finally:
            if pubsub:
                pubsub.close()

    def _arb(self):
        pass

    def _liq(self):
        pass

    def _risk(self):
        pass


if __name__ == '__main__':
    sym = SymmetricArbitrage()
    sym.run()