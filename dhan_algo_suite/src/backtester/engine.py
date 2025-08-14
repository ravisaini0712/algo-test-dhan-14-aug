from __future__ import annotations
import argparse, asyncio, math
from dataclasses import dataclass
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from loguru import logger
from ..config import settings
from ..dhan_client import DhanClient
from ..strategy.nifty_atm_option import NiftyATMOptionStrategy, Params

@dataclass
class TradeLog:
    ts_entry: datetime
    ts_exit: datetime | None
    symbol: str
    security_id: str
    side: str
    qty: int
    entry_price: float
    exit_price: float | None
    pnl: float | None
    sl_hits_today: int
    notes: str

async def fetch_spot_intraday(client: DhanClient, from_dt: str, to_dt: str, interval=5) -> pd.DataFrame:
    # Using NIFTY spot or futures continuous chosen by user; assume index instrument meta known
    data = await client.intraday(
        security_id=settings.NSE_UNDERLYING_SECURITY_ID,
        exchange_segment=settings.EXCHANGE_SEGMENT,
        instrument="INDEX",
        interval=interval,
        from_dt=from_dt,
        to_dt=to_dt,
    )
    df = pd.DataFrame({
        "open": data["open"],
        "high": data["high"],
        "low": data["low"],
        "close": data["close"],
        "ts": pd.to_datetime(data["timestamp"], unit="s", utc=True).tz_convert(settings.TIMEZONE),
    })
    return df

def month_ago(dt: datetime, months: int) -> datetime:
    # Rough month delta: 30 days * months
    return dt - timedelta(days=30*months)

async def run_backtest(months: int, lot_qty: int = 75, out_csv: str = "backtest_trades.csv"):
    now = datetime.utcnow()
    start = month_ago(now, months)
    client = DhanClient()
    strat = NiftyATMOptionStrategy(Params(lot_qty=lot_qty))
    try:
        df = await fetch_spot_intraday(client, start.strftime("%Y-%m-%d %H:%M:%S"), now.strftime("%Y-%m-%d %H:%M:%S"))
    finally:
        await client.close()

    df = df.set_index("ts").sort_index()
    # Resample to 5-min if needed
    # df = df

    trades: list[TradeLog] = []
    in_trade = False
    entry_price = None
    high_water = None
    entry_ts = None
    side = None
    security_id = "ATM_DERIVED"  # Filled when picking strike; for backtest we use synthetic ATM based on spot.

    sl_per_unit = strat.p.sl_per_unit
    daily_sl = 0

    for ts, row in df.iterrows():
        # skip outside time window
        if not (ts.time() >= pd.to_datetime(strat.p.start_time).time() and ts.time() <= pd.to_datetime(strat.p.end_time).time()):
            continue

        # reset daily counters at session start
        if ts.time() == pd.to_datetime(strat.p.start_time).time():
            daily_sl = 0
            in_trade = False
            entry_price = None
            high_water = None
            entry_ts = None
            side = None

        if daily_sl >= strat.p.max_daily_sls:
            continue

        if not in_trade:
            sig = strat.momentum_trigger(df.loc[:ts].tail(1))
            if sig.enter:
                side = sig.direction  # CALL/PUT
                # For backtest, proxy option price as (spot change) * factor; realistic modeling needs option historical data.
                entry_price = row["close"]
                high_water = entry_price
                entry_ts = ts
                in_trade = True
        else:
            # simulate option price as spot close (placeholder) and apply trail logic
            price = row["close"]
            high_water = max(high_water, price)
            tsl = strat.step_tsl(entry_price, high_water)
            stop = entry_price - sl_per_unit
            effective_sl = max(stop, tsl)

            exit_now = price <= effective_sl
            if exit_now:
                pnl_unit = price - entry_price
                pnl = pnl_unit * strat.p.lot_qty
                trades.append(TradeLog(
                    ts_entry=entry_ts, ts_exit=ts, symbol="NIFTY_OPTION_ATM", security_id=security_id,
                    side="BUY_"+side, qty=strat.p.lot_qty, entry_price=float(entry_price),
                    exit_price=float(price), pnl=float(pnl), sl_hits_today=daily_sl, notes="SL/TSL exit"
                ))
                if pnl_unit <= -sl_per_unit + 1e-6:
                    daily_sl += 1
                in_trade = False
                entry_price = None
                high_water = None
                entry_ts = None
                side = None

    # Save trades
    tdf = pd.DataFrame([t.__dict__ for t in trades])
    if not tdf.empty:
        tdf["month"] = tdf["ts_entry"].dt.to_period("M").astype(str)
        # Rolling windows
        summary = {
            "1m": tdf[tdf["ts_entry"] >= now - timedelta(days=30)]["pnl"].sum() if not tdf.empty else 0.0,
            "2m": tdf[tdf["ts_entry"] >= now - timedelta(days=60)]["pnl"].sum() if not tdf.empty else 0.0,
            "3m": tdf[tdf["ts_entry"] >= now - timedelta(days=90)]["pnl"].sum() if not tdf.empty else 0.0,
            "6m": tdf[tdf["ts_entry"] >= now - timedelta(days=180)]["pnl"].sum() if not tdf.empty else 0.0,
            "12m": tdf[tdf["ts_entry"] >= now - timedelta(days=360)]["pnl"].sum() if not tdf.empty else 0.0,
        }
        by_month = tdf.groupby("month").agg(trades=("pnl","count"), pnl=("pnl","sum")).reset_index()
        tdf.to_csv(out_csv, index=False)
        by_month.to_csv("backtest_monthly.csv", index=False)
        with open("backtest_summary.json","w") as f:
            json.dump(summary, f, indent=2, default=str)

    print(f"Saved: {out_csv}, backtest_monthly.csv, backtest_summary.json")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--months", type=int, default=6)
    ap.add_argument("--strategy", type=str, default="nifty_atm_option")
    ap.add_argument("--lot", type=int, default=75)
    args = ap.parse_args()
    asyncio.run(run_backtest(args.months, args.lot))
