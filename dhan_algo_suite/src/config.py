from pydantic import BaseModel
from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    DHAN_ACCESS_TOKEN: str
    DHAN_CLIENT_ID: str | None = None
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_CHAT_ID: str
    RUN_MODE: str = "paper"  # live|paper|backtest
    TIMEZONE: str = "Asia/Kolkata"
    EXCHANGE_SEGMENT: str = "IDX_I"  # per Dhan Annexure for NIFTY options
    NSE_UNDERLYING_SECURITY_ID: int = 13  # example: NIFTY index security id
    DB_URL: str = "sqlite:///app.db"
    LOG_LEVEL: str = "INFO"
    LIVE_WS_URL: str | None = None

    class Config:
        env_file = ".env"

settings = Settings()
