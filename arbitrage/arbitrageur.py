import logging
import os
import time
import traceback
import json
import redis
import requests

from general.logger import setup_logger
from config.binancefuture_okx_arb import TIMESTAMP, LOG_DIR, RECORDING_COIN, REDIS_HOST, REDIS_PORT, REDIS_PUBSUB, REST_MANAGER, BINANCE, OKX, TIME_IN_EXCHANGE, TIME_IN_ARB, FEE_RATE

NAME = os.path.splitext(os.path.basename(__file__))[0]
logger = setup_logger(NAME, os.path.join(LOG_DIR, f"{TIMESTAMP}_{NAME}_{RECORDING_COIN}.log"), logging.DEBUG)
logger.info(f"init {NAME}")


class SymmetricArbitrage:
    CREATE_ORDER = f"{REST_MANAGER}/create_order"

    def __init__(self, ex, symbol):
        # symmetric parameter (either A or B)
        self.ex = ex
        self.other_ex = BINANCE if ex == OKX else OKX
        self.symbol = symbol

        # status
        self.time = int(time.time() * 1000)
        self.contract = 0  # contract
        self.ask = {BINANCE: 0.0, OKX: 0.0}
        self.bid = {BINANCE: 0.0, OKX: 0.0}
        self.exchange_time = {BINANCE: 0, OKX: 0}

        # Redis
        self.redis_conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
        self.redis_channel = REDIS_PUBSUB

    def _execute_order(self, side, dry_run):
        params = {
            "symbol": self.symbol,
            "type": "market",
            "side": side,
            "amount": 1.0,
            "price": (self.ask[self.ex] + self.bid[self.ex]) / 2,  # Pseudo Price for market order
            "dry_run": dry_run
        }
        logger.info(f"request {params=}")
        res = requests.get(self.CREATE_ORDER, params=params)
        logger.info(f"{res.status_code}, {res.json()}")
        increment = 1 if side == 'buy' else -1
        self.contract = self.contract if dry_run else self.contract + increment
        logger.info(f'{self.contract=}')

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
                logger.debug(f'{data=}')
                self._update(data)
                self._arb()
                self._liq()

        except Exception as e:
            logger.info(f'Error occurred: {traceback.format_exc()}')
        finally:
            if pubsub:
                pubsub.close()

    def _risk(self):
        if abs(self.contract) >= 1:
            return False
        return True

    def _update(self, data):
        self.time = int(time.time() * 1000)

        self.ask[data['ex']] = float(data['a'])
        self.bid[data['ex']] = float(data['b'])
        self.exchange_time[data['ex']] = data['t']

    def _arb(self):
        time_gap = self.time - min(self.exchange_time[BINANCE], self.exchange_time[OKX]) < TIME_IN_ARB
        time_gap = time_gap and abs(self.exchange_time[BINANCE] - self.exchange_time[OKX]) < TIME_IN_EXCHANGE
        dry_run = not self._risk()  # If pass risk check, not use dry_run
        buy_gap = 2 * (FEE_RATE[self.other_ex] * self.bid[self.other_ex] + FEE_RATE[self.ex] * self.ask[self.ex])
        sell_gap = 2 * (FEE_RATE[self.ex] * self.bid[self.ex] + FEE_RATE[self.other_ex] * self.ask[self.other_ex])
        logger.debug(f'{time_gap=}, {dry_run=}, {buy_gap=}, {sell_gap=}')
        if time_gap and self.bid[self.other_ex] - self.ask[self.ex] > buy_gap:
            logger.info(f'arbitrage: {self.other_ex}.bid - {self.ex}.ask > {buy_gap}')
            self._execute_order('buy', dry_run)
        if time_gap and self.bid[self.ex] - self.ask[self.other_ex] > sell_gap:
            logger.info(f"arbitrage: {self.ex}.bid - {self.other_ex}.ask > {sell_gap}")
            self._execute_order('sell', dry_run)

    def _liq(self):
        logger.debug(f"Determine by liq, {self.contract=}")
        if self.contract > 0 and self.bid[self.ex] >= self.ask[self.other_ex]:
            logger.info(f'liquidate: {self.ex}.bid >= {self.other_ex}.ask')
            logger.info(f'liquidate: {self.bid[self.ex]} >= {self.ask[self.other_ex]}')
            self._execute_order('sell', False)  # Price is arbitrary
        if self.contract < 0 and self.ask[self.ex] <= self.bid[self.other_ex]:
            logger.info(f'liquidate: {self.ex}.ask <= {self.other_ex}.bid')
            logger.info(f'liquidate: {self.ask[self.ex]} <= {self.bid[self.other_ex]}')
            self._execute_order('buy', False)


