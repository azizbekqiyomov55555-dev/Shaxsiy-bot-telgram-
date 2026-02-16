import sqlite3
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

TOKEN = "8356052924:AAHeMs7mOMDFR1IB2zrO9XFfRmSY9WWlcpg"
ADMIN_ID = 8332077004
CHANNEL_ID = -100123456789

# ========= DATABASE =========
db = sqlite3.connect("market.db", check_same_thread=False)
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS ads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    name TEXT,
    price TEXT,
    description TEXT
)
""")

db.commit()

def add_user(user):
    cursor.execute("INSERT OR IGNORE INTO users VALUES (?,?)",
                   (user.id, user.first_name))
    db.commit()

def add_ad(uid, name, price, desc):
    cursor.execute("INSERT INTO ads (user_id,name,price,description) VALUES (?,?,?,?)",
                   (uid, name, price, desc))
    db.commit()

def stats():
    users = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    ads = cursor.execute("SELECT COUNT(*) FROM ads").fetchone()[0]
    return users, ads

# ========= STATES =========
(
    MENU,
    SOTISH_NAME,
    SOTISH_PRICE,
    SOTISH_DESC,
    SOTISH_PHOTO,
    OLISH,
    BROADCAST
) = range(7)

# ========= KEYBOARDS =========
menu_keyboard = [
    ["🟢 Sotish", "🛒 Olish"],
    ["📊 Statistika", "❌ Bekor qilish"]
]

menu_markup = ReplyKeyboardMarkup(menu_keyboard, resize_keyboard=True)
cancel_markup = ReplyKeyboardMarkup([["❌ Bekor qilish"]], resize_keyboard=True)

# ========= START =========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user)

    await update.message.reply_text(
        f"👋 Salom {user.first_name}!\nMarketplace botga xush kelibsiz!",
        reply_markup=menu_markup
    )
    return MENU

# ========= MENU =========
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🟢 Sotish":
        await update.message.reply_text("📦 Mahsulot nomi:", reply_markup=cancel_markup)
        return SOTISH_NAME

    if text == "🛒 Olish":
        await update.message.reply_text("🛍 Buyurtma yozing:", reply_markup=cancel_markup)
        return OLISH

    if text == "📊 Statistika":
        u, a = stats()
        await update.message.reply_text(
            f"📊 Statistika\n👥 Users: {u}\n📢 Ads: {a}",
            reply_markup=menu_markup
        )
        return MENU

    if text == "❌ Bekor qilish":
        return await cancel(update, context)

    return MENU

# ========= SOTISH FLOW =========
async def sotish_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("💰 Narx:")
    return SOTISH_PRICE

async def sotish_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["price"] = update.message.text
    await update.message.reply_text("📝 Izoh:")
    return SOTISH_DESC

async def sotish_desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["desc"] = update.message.text
    await update.message.reply_text("🖼 Rasm yuboring:")
    return SOTISH_PHOTO

async def sotish_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    photo = update.message.photo[-1].file_id

    name = context.user_data["name"]
    price = context.user_data["price"]
    desc = context.user_data["desc"]

    add_ad(user.id, name, price, desc)

    caption = (
        f"📢 YANGI E'LON\n\n"
        f"👤 {user.first_name}\n🆔 {user.id}\n\n"
        f"📦 {name}\n💰 {price}\n📝 {desc}"
    )

    await context.bot.send_photo(ADMIN_ID, photo, caption=caption)
    await context.bot.send_photo(CHANNEL_ID, photo, caption=caption)

    await update.message.reply_text("✅ E’lon joylandi!", reply_markup=menu_markup)

    context.user_data.clear()
    return MENU

# ========= OLISH =========
async def olish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    msg = (
        f"🛒 BUYURTMA\n\n"
        f"👤 {user.first_name}\n🆔 {user.id}\n\n"
        f"{update.message.text}"
    )

    await context.bot.send_message(ADMIN_ID, msg)
    await update.message.reply_text("✅ Buyurtma yuborildi!", reply_markup=menu_markup)

    return MENU

# ========= CANCEL =========
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("❌ Bekor qilindi.", reply_markup=menu_markup)
    return MENU

# ========= ADMIN =========
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    u, a = stats()
    await update.message.reply_text(f"👑 ADMIN\nUsers: {u}\nAds: {a}")

# ========= BROADCAST =========
async def broadcast_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    await update.message.reply_text("📢 Xabar yuboring:")
    return BROADCAST

async def broadcast_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    users = cursor.execute("SELECT id FROM users").fetchall()

    sent = 0
    for u in users:
        try:
            await context.bot.send_message(u[0], f"📢 ADMIN:\n{text}")
            sent += 1
        except:
            pass

    await update.message.reply_text(f"✅ Yuborildi: {sent}")
    return ConversationHandler.END

# ========= ERROR =========
async def error_handler(update, context):
    print("XATO:", context.error)

# ========= MAIN =========
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, menu)],
            SOTISH_NAME: [MessageHandler(filters.TEXT, sotish_name)],
            SOTISH_PRICE: [MessageHandler(filters.TEXT, sotish_price)],
            SOTISH_DESC: [MessageHandler(filters.TEXT, sotish_desc)],
            SOTISH_PHOTO: [MessageHandler(filters.PHOTO, sotish_photo)],
            OLISH: [MessageHandler(filters.TEXT, olish)],
        },
        fallbacks=[MessageHandler(filters.TEXT, cancel)],
    )

    broadcast_conv = ConversationHandler(
        entry_points=[CommandHandler("broadcast", broadcast_cmd)],
        states={BROADCAST: [MessageHandler(filters.TEXT, broadcast_send)]},
        fallbacks=[],
    )

    app.add_handler(conv)
    app.add_handler(broadcast_conv)
    app.add_handler(CommandHandler("admin", admin))
    app.add_error_handler(error_handler)

    print("🚀 ULTRA PRO MARKET BOT ISHLAYAPTI...")
    app.run_polling()

if __name__ == "__main__":
    main()
