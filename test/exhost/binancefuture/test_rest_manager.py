import logging
import unittest
import httpx
from logger import setup_logger

class TestHostedFastAPI(unittest.IsolatedAsyncioTestCase):
    BASE_URL = 'http://127.0.0.1:8000'  # Replace with your hosted app URL
    logger = setup_logger(__name__, None, logging.INFO)
    async def asyncSetUp(self):
        self.client = httpx.AsyncClient()

    async def asyncTearDown(self):
        await self.client.aclose()

    async def test_test(self):
        response = await self.client.get(f"{self.BASE_URL}/ping")
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertIn('pong', json_data)
        self.logger.info(f'{json_data=}')

    async def test_create_order(self):
        params = {
            "symbol": "ETH/USDT",
            "type": "limit",
            "side": "sell",
            "amount": 0.5,
            "price": 2000.0
        }
        response = await self.client.get(f"{self.BASE_URL}/create_order", params=params)
        json_data = response.json()
        self.logger.info(f'{json_data=}')
        self.assertEqual(response.status_code, 200)

        # Additional assertions based on the expected response structure
        json_data = response.json()
        self.assertIn('id', json_data)
        self.assertIn('status', json_data)
        self.assertEqual(json_data['symbol'], 'BTC/USDT')


if __name__ == "__main__":
    unittest.main()
