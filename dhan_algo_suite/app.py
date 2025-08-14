from fastapi import FastAPI
import asyncio
import os

app = FastAPI()

# Import the bot
from dhan_algo_suite.telegram_bot import build_and_start_bot

bot_task = None

@app.on_event("startup")
async def startup_event():
    global bot_task
    loop = asyncio.get_event_loop()
    bot_task = loop.create_task(build_and_start_bot())
    print("✅ Telegram bot polling started")

@app.on_event("shutdown")
async def shutdown_event():
    global bot_task
    if bot_task:
        bot_task.cancel()
    print("🛑 Telegram bot stopped")

@app.get("/")
async def root():
    return {"status": "running"}
