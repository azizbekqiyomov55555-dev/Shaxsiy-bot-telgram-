from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8356052924:AAHeMs7mOMDFR1IB2zrO9XFfRmSY9WWlcpg"

# Tugmalar
keyboard = [
    ["🟢 Sotish", "🟢 Olish"]
]

markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Kerakli bo‘limni tanlang 👇",
        reply_markup=markup
    )

# Tugmalarni ushlash
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🟢 Sotish":
        await update.message.reply_text("Sotish bo‘limiga kirdingiz 💰")

    elif text == "🟢 Olish":
        await update.message.reply_text("Olish bo‘limiga kirdingiz 🛒")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot ishlayapti...")
    app.run_polling()

if __name__ == "__main__":
    main()
