from __future__ import annotations
import httpx, time, asyncio, json
from typing import Any, Dict, Optional
from loguru import logger
from .config import settings

API_BASE = "https://api.dhan.co/v2"

def _headers(include_client=False):
    h = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "access-token": settings.DHAN_ACCESS_TOKEN,
    }
    if include_client and settings.DHAN_CLIENT_ID:
        h["client-id"] = settings.DHAN_CLIENT_ID
    return h

class DhanClient:
    def __init__(self, timeout: float = 15.0):
        self.http = httpx.AsyncClient(timeout=timeout)

    async def close(self):
        await self.http.aclose()

    # --- Orders ---
    async def place_order(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        r = await self.http.post(f"{API_BASE}/orders", json=payload, headers=_headers())
        r.raise_for_status()
        return r.json()

    async def modify_order(self, order_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        r = await self.http.put(f"{API_BASE}/orders/{order_id}", json=payload, headers=_headers())
        r.raise_for_status()
        return r.json()

    async def cancel_order(self, order_id: str) -> Dict[str, Any]:
        r = await self.http.delete(f"{API_BASE}/orders/{order_id}", headers=_headers())
        r.raise_for_status()
        return r.json()

    async def order_book(self):
        r = await self.http.get(f"{API_BASE}/orders", headers=_headers())
        r.raise_for_status()
        return r.json()

    async def trade_book(self):
        r = await self.http.get(f"{API_BASE}/trades", headers=_headers())
        r.raise_for_status()
        return r.json()

    # --- Market Quote ---
    async def market_quote(self, security_id: int, exchange_segment: str):
        # POST /marketfeed/quotes or as per docs 'Market Quote' page
        # Dhan v2 page shows Market Quote endpoint group; request body may accept list.
        # We'll support single security for simplicity here.
        url = f"{API_BASE}/marketfeed/quotes"
        payload = {"securityIds": [str(security_id)], "exchangeSegment": exchange_segment}
        r = await self.http.post(url, json=payload, headers=_headers(include_client=True))
        r.raise_for_status()
        return r.json()

    # --- Historical ---
    async def intraday(self, security_id: int, exchange_segment: str, instrument: str, interval: int,
                       from_dt: str, to_dt: str, oi: bool=False):
        url = f"{API_BASE}/charts/intraday"
        payload = {
            "securityId": str(security_id),
            "exchangeSegment": exchange_segment,
            "instrument": instrument,
            "interval": str(interval),
            "oi": oi,
            "fromDate": from_dt,
            "toDate": to_dt
        }
        r = await self.http.post(url, json=payload, headers=_headers())
        r.raise_for_status()
        return r.json()

    # --- Option Chain ---
    async def option_chain(self, underlying_sec_id: int, underlying_seg: str, expiry: str):
        url = f"{API_BASE}/optionchain"
        payload = {"UnderlyingScrip": underlying_sec_id, "UnderlyingSeg": underlying_seg, "Expiry": expiry}
        r = await self.http.post(url, json=payload, headers=_headers(include_client=True))
        r.raise_for_status()
        return r.json()

    async def expiry_list(self, underlying_sec_id: int, underlying_seg: str):
        url = f"{API_BASE}/optionchain/expirylist"
        payload = {"UnderlyingScrip": underlying_sec_id, "UnderlyingSeg": underlying_seg}
        r = await self.http.post(url, json=payload, headers=_headers(include_client=True))
        r.raise_for_status()
        return r.json()

    # --- Websocket (Live Market Feed) ---
    async def live_feed(self, on_message):
        # Dhan docs provide Live Market Feed; URL may change. Supply via env if needed.
        ws_url = settings.LIVE_WS_URL or "wss://livefeeds.dhan.co/v2/ws"
        import websockets
        async with websockets.connect(ws_url, extra_headers=_headers(include_client=True)) as ws:
            # Typically, you must send a subscribe message after connect.
            # This structure is documented in Dhan Live Market Feed page.
            # Example subscription payload; user should pass list of tokens elsewhere.
            await ws.send(json.dumps({"action": "subscribe", "instruments": []}))
            async for msg in ws:
                try:
                    data = json.loads(msg)
                except json.JSONDecodeError:
                    data = {"raw": msg}
                await on_message(data)
