import asyncio, json
from datetime import datetime
from loguru import logger
from ..config import settings
from ..dhan_client import DhanClient
from ..strategy.nifty_atm_option import NiftyATMOptionStrategy, Params
from ..utils import in_trading_window

async def paper_trade():
    client = DhanClient()
    strat = NiftyATMOptionStrategy(Params())
    async def on_msg(msg):
        # process ticks and simulate; placeholder for user to implement based on Dhan WS payload
        pass
    # If WS URL unavailable, poll quotes
    try:
        # Example polling: every 3s for underlying
        while True:
            now = datetime.utcnow()
            if not in_trading_window(now, settings.TIMEZONE):
                await asyncio.sleep(5)
                continue
            q = await client.market_quote(settings.NSE_UNDERLYING_SECURITY_ID, settings.EXCHANGE_SEGMENT)
            # TODO: convert q to candle aggregator and run strategy
            await asyncio.sleep(3)
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(paper_trade())
