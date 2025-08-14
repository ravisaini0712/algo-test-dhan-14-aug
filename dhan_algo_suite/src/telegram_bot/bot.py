# dhan_algo_suite/bot.py

import os
import asyncio
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import Conflict

# ===== Main Menu Keyboard =====
main_menu_keyboard = [
    ["📊 Balance", "📂 Positions"],
    ["📜 Orders", "🏓 Ping"],
    ["🛒 Buy", "💰 Sell"]
]
main_menu_markup = ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True)

# ===== Command Handlers =====
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 Dhan Algo Bot is live!\nChoose an option:",
        reply_markup=main_menu_markup
    )

async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("pong 🏓")

async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Balance: ₹100,000 (dummy data)")

async def positions_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Positions: None (dummy)")

async def orders_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Orders: None (dummy)")

async def buy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send the symbol and quantity to buy (dummy flow)")

async def sell_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send the symbol and quantity to sell (dummy flow)")

# ===== Text Button Handler =====
async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "📊 Balance":
        await balance_command(update, context)
    elif text == "📂 Positions":
        await positions_command(update, context)
    elif text == "📜 Orders":
        await orders_command(update, context)
    elif text == "🏓 Ping":
        await ping_command(update, context)
    elif text == "🛒 Buy":
        await buy_command(update, context)
    elif text == "💰 Sell":
        await sell_command(update, context)
    else:
        await update.message.reply_text("Please choose from the menu.")

# ===== Bot Runner =====
async def run_bot():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN not set in env variables")

    app = ApplicationBuilder().token(token).build()

    # Start command
    app.add_handler(CommandHandler("start", start_command))
    # Text-based menu handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu))

    try:
        print("Starting Telegram bot polling...")
        await app.run_polling()
    except Conflict:
        print("Conflict: Another instance is running. Stopping this one.")

if __name__ == "__main__":
    asyncio.run(run_bot())
