from datetime import datetime, time, timedelta
import pytz

def in_trading_window(now: datetime, tz: str = "Asia/Kolkata") -> bool:
    z = pytz.timezone(tz)
    n = now.astimezone(z)
    start = z.localize(datetime(n.year, n.month, n.day, 9, 15)).timetz()
    end   = z.localize(datetime(n.year, n.month, n.day, 15, 15)).timetz()
    return start <= n.timetz() <= end

def after_cutoff(now: datetime, tz: str = "Asia/Kolkata") -> bool:
    z = pytz.timezone(tz)
    n = now.astimezone(z)
    cutoff = z.localize(datetime(n.year, n.month, n.day, 15, 15)).timetz()
    return n.timetz() >= cutoff

def floor_to_interval(ts: datetime, minutes: int = 5) -> datetime:
    return ts.replace(second=0, microsecond=0, minute=(ts.minute // minutes)*minutes)
