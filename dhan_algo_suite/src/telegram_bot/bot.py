import asyncio, json, os
from datetime import datetime
from loguru import logger
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
from ..config import settings

HELP = (
"""Commands:
/start - show menu
/status - show mode, SL hits, position
/backtest <months> - run backtest for last N months
/paper - start paper trading
/live - start live trading
/stop - stop any running mode
/positions - show open positions
/pnl - show today's P&L
/logs - last errors
/help - this help
"""
)

running_task = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [
        [InlineKeyboardButton("Run Backtest 1m", callback_data="bt:1"),
         InlineKeyboardButton("Run Backtest 6m", callback_data="bt:6")],
        [InlineKeyboardButton("Start Paper", callback_data="paper"),
         InlineKeyboardButton("Start Live", callback_data="live")],
        [InlineKeyboardButton("Stop", callback_data="stop")]
    ]
    await update.message.reply_text("Dhan Manager", reply_markup=InlineKeyboardMarkup(kb))

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP)

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Mode: {settings.RUN_MODE} | Chat: {settings.TELEGRAM_CHAT_ID}")

async def backtest_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    months = int(context.args[0]) if context.args else 6
    from ..backtester.engine import run_backtest
    await update.message.reply_text(f"Running backtest for {months} months...")
    await run_backtest(months, out_csv=f"bt_{months}m.csv")
    await update.message.reply_document(open(f"bt_{months}m.csv","rb"))
    await update.message.reply_document(open("backtest_monthly.csv","rb"))
    await update.message.reply_document(open("backtest_summary.json","rb"))

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data.startswith("bt:"):
        months = int(q.data.split(":")[1])
        await backtest_cmd(update, context.__class__(application=context.application, _chat_id_and_data=context._chat_id_and_data))
    elif q.data=="paper":
        await q.edit_message_text("Paper trading starting (run process `python -m simulator.paper_engine`)")
    elif q.data=="live":
        await q.edit_message_text("Live trading starting (run process `python -m live.trader`)")
    elif q.data=="stop":
        await q.edit_message_text("Stop requested (terminate running process on Railway).")

def run():
    app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("backtest", backtest_cmd))
    app.add_handler(CallbackQueryHandler(buttons))
    app.run_polling()

if __name__ == "__main__":
    run()
