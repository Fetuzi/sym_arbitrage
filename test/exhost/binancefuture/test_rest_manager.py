import logging
import unittest
import httpx
from config.binancefuture_okx_arb import REST_MANAGER
from general.logger import setup_logger

class TestHostedFastAPI(unittest.IsolatedAsyncioTestCase):
    BASE_URL = REST_MANAGER  # Replace with your hosted app URL
    # BASE_URL = "http://ec2-52-198-41-165.ap-northeast-1.compute.amazonaws.com:8080"
    logger = setup_logger(__name__, None, logging.INFO)
    async def asyncSetUp(self):
        self.client = httpx.AsyncClient()

    async def asyncTearDown(self):
        await self.client.aclose()

    async def test_ping(self):
        response = await self.client.get(f"{self.BASE_URL}/ping")
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertIn('pong', json_data)
        self.logger.info(f'{json_data=}')

    async def test_create_order(self):
        params = {
            "symbol": "LTCUSDT",
            "type": "limit",
            "side": "buy",
            "amount": 1,
            "price": 55.0,
            "dry_run": False
        }

        res = await self.client.get(f"{self.BASE_URL}/create_order", params=params)
        self.logger.info("async call before using response")
        self.logger.info(f"{res=}")


if __name__ == "__main__":
    unittest.main()
