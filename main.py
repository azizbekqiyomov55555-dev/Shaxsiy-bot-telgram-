from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "BOT_TOKENINGIZNI_BU_YERGA_QOYING"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salom 👋 Bot ishlayapti!")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    print("Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
