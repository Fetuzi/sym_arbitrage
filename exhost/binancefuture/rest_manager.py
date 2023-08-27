import os
import json
from fastapi import FastAPI

from config.binancefuture_kucoin_arb import LOG_DIR, TIMESTAMP
from logger import setup_logger


app = FastAPI()

logger = setup_logger(__name__, os.path.join(LOG_DIR, f"{TIMESTAMP}_{__name__}.log"))
logger.info(f"init {__name__}")

@app.get("/test")
async def test():
    logger.info("test is called!")
    return {"Hello": "World"}
