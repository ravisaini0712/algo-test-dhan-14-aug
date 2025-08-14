import asyncio, json, math
from datetime import datetime
from loguru import logger
from ..config import settings
from ..dhan_client import DhanClient
from ..strategy.nifty_atm_option import NiftyATMOptionStrategy, Params
from ..utils import in_trading_window, after_cutoff

class LiveTrader:
    def __init__(self):
        self.client = DhanClient()
        self.strat = NiftyATMOptionStrategy(Params())
        self.sl_hits = 0
        self.position = None  # store order ids and prices

    async def place_entry(self, security_id: str, side: str, qty: int, price: float | None=None):
        payload = {
            "dhanClientId": settings.DHAN_CLIENT_ID,
            "transactionType": "BUY",
            "exchangeSegment": settings.EXCHANGE_SEGMENT,
            "productType": "INTRADAY",
            "orderType": "MARKET",
            "validity": "DAY",
            "securityId": str(security_id),
            "quantity": qty,
        }
        resp = await self.client.place_order(payload)
        return resp

    async def loop(self):
        # Simplified live loop
        try:
            while True:
                now = datetime.utcnow()
                if after_cutoff(now, settings.TIMEZONE) or self.sl_hits >= self.strat.p.max_daily_sls:
                    await asyncio.sleep(5); continue
                # TODO: build candles from Market Quote or WS to detect momentum and then pick ATM strike via Option Chain
                await asyncio.sleep(3)
        finally:
            await self.client.close()

if __name__ == "__main__":
    asyncio.run(LiveTrader().loop())
