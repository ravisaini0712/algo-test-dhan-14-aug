import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# =============================
# COMMAND HANDLERS
# =============================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 Dhan Algo Bot is live and running!\n\n"
        "Available commands:\n"
        "/balance - Check account balance\n"
        "/positions - View open positions\n"
        "/orders - View recent orders\n"
        "/buy <symbol> <qty> - Place a buy order\n"
        "/sell <symbol> <qty> - Place a sell order\n"
        "/help - Show this help menu"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ℹ️ Available commands:\n"
        "/balance - Check account balance\n"
        "/positions - View open positions\n"
        "/orders - View recent orders\n"
        "/buy <symbol> <qty> - Place a buy order\n"
        "/sell <symbol> <qty> - Place a sell order"
    )

async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # TODO: Replace this with actual Dhan API call
    balance = 100000.00  # Dummy value
    await update.message.reply_text(f"💰 Account Balance: ₹{balance:,.2f}")

async def positions_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # TODO: Replace with real positions from Dhan API
    positions = [
        {"symbol": "RELIANCE", "qty": 10, "avg_price": 2500},
        {"symbol": "INFY", "qty": 5, "avg_price": 1500}
    ]
    if positions:
        text = "📊 Open Positions:\n" + "\n".join(
            [f"{p['symbol']} - {p['qty']} @ ₹{p['avg_price']}" for p in positions]
        )
    else:
        text = "📊 No open positions."
    await update.message.reply_text(text)

async def orders_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # TODO: Replace with real orders from Dhan API
    orders = [
        {"symbol": "TCS", "side": "BUY", "qty": 2, "status": "COMPLETED"},
        {"symbol": "HDFC", "side": "SELL", "qty": 1, "status": "PENDING"}
    ]
    if orders:
        text = "📜 Recent Orders:\n" + "\n".join(
            [f"{o['side']} {o['symbol']} x{o['qty']} - {o['status']}" for o in orders]
        )
    else:
        text = "📜 No recent orders."
    await update.message.reply_text(text)

async def buy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /buy <symbol> <qty>")
        return
    symbol = context.args[0].upper()
    qty = int(context.args[1])
    # TODO: Place buy order via Dhan API
    await update.message.reply_text(f"✅ Buy order placed: {symbol} x{qty}")

async def sell_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /sell <symbol> <qty>")
        return
    symbol = context.args[0].upper()
    qty = int(context.args[1])
    # TODO: Place sell order via Dhan API
    await update.message.reply_text(f"✅ Sell order placed: {symbol} x{qty}")

# =============================
# MAIN APPLICATION
# =============================

def run_bot():
    if not TELEGRAM_TOKEN:
        raise ValueError("❌ TELEGRAM_TOKEN not found in environment variables.")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("balance", balance_command))
    app.add_handler(CommandHandler("positions", positions_command))
    app.add_handler(CommandHandler("orders", orders_command))
    app.add_handler(CommandHandler("buy", buy_command))
    app.add_handler(CommandHandler("sell", sell_command))

    print("✅ Telegram bot polling started")
    app.run_polling()

if __name__ == "__main__":
    run_bot()
