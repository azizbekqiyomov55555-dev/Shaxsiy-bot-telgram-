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

TOKEN = "8356052924:AAF9dPkpBS5U5Svq9rIvxTsZ14k9RGLnOTs"
ADMIN_ID = 8332077004
CHANNEL_ID = -100123456789

# ===== DATABASE =====
db = sqlite3.connect("kino.db", check_same_thread=False)
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS movies(
code TEXT PRIMARY KEY,
title TEXT,
file_id TEXT
)
""")
db.commit()

# ===== STATES =====
MENU, ADD_CODE, ADD_TITLE, ADD_VIDEO, DELETE = range(5)

# ===== KEYBOARD =====
menu = ReplyKeyboardMarkup(
    [["🎬 Kino olish"], ["❌ Bekor qilish"]],
    resize_keyboard=True
)

cancel = ReplyKeyboardMarkup([["❌ Bekor qilish"]], resize_keyboard=True)

# ===== START =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 Kino botga xush kelibsiz!\nKino kodini yuboring:",
        reply_markup=menu
    )
    return MENU

# ===== USER SEARCH =====
async def user_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "❌ Bekor qilish":
        return await cancel_flow(update, context)

    movie = cursor.execute(
        "SELECT title,file_id FROM movies WHERE code=?",
        (text,)
    ).fetchone()

    if movie:
        title, file_id = movie
        await update.message.reply_video(file_id, caption=f"🎬 {title}")
    else:
        await update.message.reply_text("❌ Kino topilmadi")

    return MENU

# ===== ADMIN ADD MOVIE =====
async def add_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    await update.message.reply_text("🎬 Kino kodini yozing:", reply_markup=cancel)
    return ADD_CODE

async def add_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["code"] = update.message.text
    await update.message.reply_text("🎬 Kino nomi:")
    return ADD_TITLE

async def add_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["title"] = update.message.text
    await update.message.reply_text("📤 Kino video yuboring:")
    return ADD_VIDEO

async def add_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    video = update.message.video.file_id
    code = context.user_data["code"]
    title = context.user_data["title"]

    cursor.execute(
        "INSERT OR REPLACE INTO movies VALUES (?,?,?)",
        (code, title, video)
    )
    db.commit()

    caption = f"🎬 {title}\n📌 Kod: {code}"

    # Kanalga post
    await context.bot.send_video(CHANNEL_ID, video, caption=caption)

    await update.message.reply_text("✅ Kino saqlandi va kanalga joylandi!", reply_markup=menu)

    context.user_data.clear()
    return MENU

# ===== DELETE MOVIE =====
async def delete_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    await update.message.reply_text("🗑 O‘chirish uchun kod yuboring:", reply_markup=cancel)
    return DELETE

async def delete_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = update.message.text

    cursor.execute("DELETE FROM movies WHERE code=?", (code,))
    db.commit()

    await update.message.reply_text("✅ Kino o‘chirildi!", reply_markup=menu)
    return MENU

# ===== STATS =====
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    total = cursor.execute("SELECT COUNT(*) FROM movies").fetchone()[0]

    await update.message.reply_text(f"📊 Bazadagi kinolar: {total}")

# ===== CANCEL =====
async def cancel_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("❌ Bekor qilindi", reply_markup=menu)
    return MENU

# ===== MAIN =====
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    user_conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, user_menu)],
        },
        fallbacks=[MessageHandler(filters.TEXT, cancel_flow)],
    )

    add_conv = ConversationHandler(
        entry_points=[CommandHandler("addmovie", add_movie)],
        states={
            ADD_CODE: [MessageHandler(filters.TEXT, add_code)],
            ADD_TITLE: [MessageHandler(filters.TEXT, add_title)],
            ADD_VIDEO: [MessageHandler(filters.VIDEO, add_video)],
        },
        fallbacks=[MessageHandler(filters.TEXT, cancel_flow)],
    )

    delete_conv = ConversationHandler(
        entry_points=[CommandHandler("deletemovie", delete_movie)],
        states={DELETE: [MessageHandler(filters.TEXT, delete_code)]},
        fallbacks=[MessageHandler(filters.TEXT, cancel_flow)],
    )

    app.add_handler(user_conv)
    app.add_handler(add_conv)
    app.add_handler(delete_conv)
    app.add_handler(CommandHandler("stats", stats))

    print("🎬 PRO kino bot ishlayapti...")
    app.run_polling()

if __name__ == "__main__":
    main()
