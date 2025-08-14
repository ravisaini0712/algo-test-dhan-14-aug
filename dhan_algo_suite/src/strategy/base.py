from dataclasses import dataclass
from typing import Optional

@dataclass
class TradeAction:
    side: str            # 'BUY' or 'SELL'
    product: str         # 'INTRADAY' or others
    order_type: str      # 'MARKET'/'LIMIT'
    security_id: str
    quantity: int
    price: float | None = None
    sl_price: float | None = None

@dataclass
class StrategySignal:
    enter: bool
    direction: Optional[str] = None  # 'CALL' or 'PUT' or 'FUT_LONG'/'FUT_SHORT'
    reason: str = ""
