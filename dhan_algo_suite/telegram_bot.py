import os
from telegram.ext import ApplicationBuilder, CommandHandler

async def start_command(update, context):
    await update.message.reply_text("✅ Bot is alive and running on Railway!")

async def build_and_start_bot():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN not set in environment variables")

    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start_command))

    # run_polling() blocks, so in async we do it this way
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await app.updater.wait()
