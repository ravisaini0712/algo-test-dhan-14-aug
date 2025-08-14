from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import pandas as pd
from ..strategy.base import StrategySignal

@dataclass
class Params:
    lot_qty: int = 75
    sl_per_unit: float = 20.0
    tsl_steps: list[tuple[float, float]] = field(default_factory=lambda: [
        (5, 10),   # move SL +10 when +5 in favor
        (13, 20),  # move SL to cost when +13
        (20, 30),  # move SL to +10 when +20
    ])
    max_daily_sls: int = 3
    start_time: str = "09:15"
    end_time: str = "15:15"
    big_candle_points: float = 15.0
    timeframe_min: int = 5
    slightly_itm: bool = False

class NiftyATMOptionStrategy:
    def __init__(self, params: Params):
        self.p = params
        self.daily_sl_hits = 0
        self.in_position = False

    def reset_day(self):
        self.daily_sl_hits = 0
        self.in_position = False

    def momentum_trigger(self, spot_candles: pd.DataFrame) -> StrategySignal:
        # Expect dataframe with columns: ['ts','open','high','low','close']
        last = spot_candles.iloc[-1]
        body = last['close'] - last['open']
        if abs(body) >= self.p.big_candle_points:
            direction = "CALL" if body > 0 else "PUT"
            return StrategySignal(enter=True, direction=direction, reason=f"Momentum {body:.1f}pts")
        return StrategySignal(enter=False)

    def step_tsl(self, entry_price: float, high_water: float) -> float:
        tsl = entry_price - self.p.sl_per_unit  # initial SL
        move = high_water - entry_price
        for step_gain, new_sl_offset in self.p.tsl_steps:
            if move >= step_gain:
                tsl = max(tsl, entry_price - self.p.sl_per_unit + (new_sl_offset))
        return tsl
