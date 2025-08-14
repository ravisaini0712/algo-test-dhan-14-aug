import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from fastapi import FastAPI, Request
import uvicorn

# Create FastAPI app
app = FastAPI()

# ====== BUTTON HANDLERS ======
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📈 Place Buy Order", callback_data="buy")],
        [InlineKeyboardButton("📉 Place Sell Order", callback_data="sell")],
        [InlineKeyboardButton("💼 Check Positions", callback_data="positions")],
        [InlineKeyboardButton("❌ Exit All", callback_data="exit_all")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "✅ Bot is alive!\nSelect an action:",
        reply_markup=reply_markup
    )

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "buy":
        await query.edit_message_text("📈 Buy order placed! (Dummy action for now)")
        # TODO: Call your Dhan buy order API here

    elif query.data == "sell":
        await query.edit_message_text("📉 Sell order placed! (Dummy action for now)")
        # TODO: Call your Dhan sell order API here

    elif query.data == "positions":
        await query.edit_message_text("💼 Fetching positions...")
        # TODO: Call your Dhan positions API here

    elif query.data == "exit_all":
        await query.edit_message_text("❌ Exiting all positions...")
        # TODO: Call your Dhan exit all API here

# ====== TELEGRAM BOT SETUP ======
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not set in environment variables")

telegram_app = ApplicationBuilder().token(TOKEN).build()
telegram_app.add_handler(CommandHandler("start", start_command))
telegram_app.add_handler(CallbackQueryHandler(button_click))

# ====== FASTAPI WEBHOOK ENDPOINT ======
@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    await telegram_app.update_queue.put(data)
    return {"status": "ok"}

# ====== SETUP WEBHOOK ON STARTUP ======
@app.on_event("startup")
async def on_startup():
    webhook_url = os.getenv("WEBHOOK_URL")  # e.g. https://your-railway-app.up.railway.app/webhook
    if not webhook_url:
        raise ValueError("WEBHOOK_URL not set in environment variables")
    await telegram_app.bot.set_webhook(webhook_url)
    print(f"✅ Webhook set to: {webhook_url}")

# ====== MAIN RUN ======
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
