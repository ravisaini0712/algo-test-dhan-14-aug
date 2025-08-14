import os
from fastapi import FastAPI, Request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

# --- Environment Variables ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Set in Railway variables
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # e.g., https://yourapp.railway.app

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set in environment variables.")

if not WEBHOOK_URL:
    raise ValueError("WEBHOOK_URL is not set in environment variables.")

# --- FastAPI app ---
app = FastAPI()

# --- Telegram bot app ---
telegram_app = Application.builder().token(TELEGRAM_TOKEN).build()

# --- Handlers ---
async def start(update: Update, context):
    keyboard = [
        [InlineKeyboardButton("📈 Buy", callback_data="buy")],
        [InlineKeyboardButton("📉 Sell", callback_data="sell")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Welcome! Choose an action:", reply_markup=reply_markup)

async def button_handler(update: Update, context):
    query = update.callback_query
    await query.answer()

    if query.data == "buy":
        await query.edit_message_text("✅ Buy order placed!")
    elif query.data == "sell":
        await query.edit_message_text("✅ Sell order placed!")
    elif query.data == "cancel":
        await query.edit_message_text("❌ Order canceled!")

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CallbackQueryHandler(button_handler))

# --- Webhook endpoint for Telegram ---
@app.post(f"/{TELEGRAM_TOKEN}")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"status": "ok"}

# --- Function for app.py ---
def build_and_start_bot():
    """Called by app.py to set webhook when service starts."""
    webhook_url = f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}"
    telegram_app.bot.set_webhook(webhook_url)
    print(f"✅ Webhook set to: {webhook_url}")
