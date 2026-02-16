import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    await update.message.reply_text(
        f"Salom {user_name}! 👋\nBotimizga xush kelibsiz!"
    )

if __name__ == "__main__":
    TOKEN = "8356052924:AAG0auwyE4QSXLqI6adK8CUOfwzd7DWnihY"

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    print("Bot ishga tushdi...")
    app.run_polling()
