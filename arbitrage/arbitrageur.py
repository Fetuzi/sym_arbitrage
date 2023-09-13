import logging
import os
import time
import traceback
import json
import redis
from collections import deque
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
        self.queue = {self.ex: deque(), self.other_ex: deque()}

        # Redis
        self.redis_conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
        self.redis_channel = REDIS_PUBSUB

    def _execute_order(self, side, dry_run):
        params = {
            "symbol": self.symbol,
            "type": "market",
            "side": side,
            "amount": 1.0,
            "price": None,
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
                if self.queue[BINANCE] and self.queue[OKX]:
                    pair, ask, bid = self._pair()
                    logger.debug(f"Selected {pair=}, {ask=} and {bid=}")
                    self._arb(pair, ask, bid)
                    self._liq(ask, bid)
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
        self.queue[data['ex']].append(data)

    def _pair(self):
        pair = [self.queue[BINANCE][0], self.queue[OKX][0]]
        pair.sort(key=lambda data: data['t'])
        max_t = pair[1]['t']
        min_ex = pair[0]['ex']
        logger.debug(f'Initial {pair=}')
        while self.queue[min_ex] and self.queue[min_ex][0]['t'] < max_t:
            pair[0] = self.queue[min_ex].popleft()
            logger.debug(f'pop {pair[0]}')
        bid = {pair[0]['ex']: float(pair[0]['b']), pair[1]['ex']: float(pair[1]['b'])}
        ask = {pair[0]['ex']: float(pair[0]['a']), pair[1]['ex']: float(pair[1]['a'])}
        return pair, ask, bid

    def _arb(self, pair, ask, bid):
        buy_gap = 2 * (FEE_RATE[self.other_ex] * bid[self.other_ex] + FEE_RATE[self.ex] * ask[self.ex])
        sell_gap = 2 * (FEE_RATE[self.ex] * bid[self.ex] + FEE_RATE[self.other_ex] * ask[self.other_ex])

        time_gap = self.time - pair[0]['t'] < TIME_IN_ARB
        time_gap = time_gap and pair[1]['t'] - pair[0]['t'] < TIME_IN_EXCHANGE
        dry_run = not self._risk()  # If pass risk check, not use dry_run

        logger.debug(f'{time_gap=}, {dry_run=}, {buy_gap=}, {sell_gap=}')

        if time_gap and bid[self.other_ex] - ask[self.ex] > buy_gap:
            logger.info(f'arbitrage: {self.other_ex}.bid - {self.ex}.ask > {buy_gap}')
            self._execute_order('buy', dry_run)
        if time_gap and bid[self.ex] - ask[self.other_ex] > sell_gap:
            logger.info(f"arbitrage: {self.ex}.bid - {self.other_ex}.ask > {sell_gap}")
            self._execute_order('sell', dry_run)

    def _liq(self, ask, bid):

        # liq_gap = FEE_RATE[self.other_ex] * bid[self.other_ex] + FEE_RATE[self.ex] * ask[self.ex]
        logger.debug(f"Determine by liq, {self.contract=}")
        # if self.contract > 0 and self.bid[self.ex] - self.ask[self.other_ex] <= liq_gap:
        if self.contract > 0 and bid[self.ex] >= ask[self.other_ex]:
            logger.info(f'liquidate: {self.ex}.bid >= {self.other_ex}.ask')
            logger.info(f'liquidate: {bid[self.ex]} >= {ask[self.other_ex]}')
            self._execute_order('sell', False)  # Price is arbitrary
        # if self.contract < 0 and self.bid[self.other_ex] - self.ask[self.ex] <= liq_gap:
        if self.contract < 0 and ask[self.ex] <= bid[self.other_ex]:
            logger.info(f'liquidate: {self.ex}.ask <= {self.other_ex}.bid')
            logger.info(f'liquidate: {ask[self.ex]} <= {bid[self.other_ex]}')
            self._execute_order('buy', False)


