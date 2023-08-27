import os
import time
from fastapi import FastAPI, Depends, HTTPException
import ccxt.async_support as ccxt
from config.binancefuture_kucoin_arb import LOG_DIR, TIMESTAMP, BINANCE_API_KEY, BINANCE_SECRET_KEY
from logger import setup_logger


app = FastAPI()

binance = ccxt.binance({
    'apiKey': BINANCE_API_KEY,
    'secret': BINANCE_SECRET_KEY,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future',
        }
})

logger = setup_logger(__name__, os.path.join(LOG_DIR, f"{TIMESTAMP}_{__name__}.log"))
logger.info(f"init {__name__}")

async def get_binance_client():
    return binance

@app.get("/ping")
async def test():
    logger.info("ping is called!")
    return {"pong": int(time.time() * 1000)}

@app.get("/create_order")
async def create_order(
        symbol: str,
        type: str,
        side: str,
        amount: float,
        price: float,
        binance: ccxt.binance = Depends(get_binance_client)
):
    try:
        logger.info(f'Send request: {symbol=}, {type=}, {side=}, {amount=}, {price=}')
        order = await binance.create_order(symbol, type, side, amount, price)
        logger.info(f'{order=}')

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

