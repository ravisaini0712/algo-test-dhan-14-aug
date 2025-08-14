import pandas as pd
from datetime import datetime, timedelta

def summarize(trades_csv: str = "backtest_trades.csv"):
    df = pd.read_csv(trades_csv, parse_dates=["ts_entry","ts_exit"])
    df["month"] = df["ts_entry"].dt.to_period("M").astype(str)
    by_month = df.groupby("month").agg(trades=("pnl","count"), pnl=("pnl","sum")).reset_index()
    now = df["ts_entry"].max() if not df.empty else datetime.utcnow()
    summary = {
        "1m": df[df["ts_entry"] >= now - timedelta(days=30)]["pnl"].sum(),
        "2m": df[df["ts_entry"] >= now - timedelta(days=60)]["pnl"].sum(),
        "3m": df[df["ts_entry"] >= now - timedelta(days=90)]["pnl"].sum(),
        "6m": df[df["ts_entry"] >= now - timedelta(days=180)]["pnl"].sum(),
        "12m": df[df["ts_entry"] >= now - timedelta(days=360)]["pnl"].sum(),
    }
    by_month.to_csv("report_monthly.csv", index=False)
    pd.Series(summary).to_csv("report_summary.csv")
    return by_month, summary

if __name__ == "__main__":
    print(summarize())
