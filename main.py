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

TOKEN = "7741239279:AAGRIDHiP_2Vt66_zRv7ZJRXMTKbJamJ3v0"
ADMIN_ID = 8332077004

# ===== DATABASE =====
db = sqlite3.connect("kino.db", check_same_thread=False)
cur = db.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY)")
cur.execute("""
CREATE TABLE IF NOT EXISTS movies(
code TEXT PRIMARY KEY,
title TEXT,
file_id TEXT
)
""")
db.commit()

def add_user(uid):
    cur.execute("INSERT OR IGNORE INTO users VALUES(?)", (uid,))
    db.commit()

# ===== STATES =====
MENU, ADD_CODE, ADD_TITLE, ADD_VIDEO, SEARCH, BROADCAST = range(6)

# ===== KEYBOARD =====
menu_markup = ReplyKeyboardMarkup(
    [["🎬 Kod bilan olish", "🔍 Qidirish"],
     ["📃 Ro‘yxat", "❌ Bekor"]],
    resize_keyboard=True
)

cancel_markup = ReplyKeyboardMarkup([["❌ Bekor"]], resize_keyboard=True)

# ===== START =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_user(update.effective_user.id)

    await update.message.reply_text(
        "🎬 Kino botga xush kelibsiz!",
        reply_markup=menu_markup
    )
    return MENU

# ===== USER MENU =====
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🎬 Kod bilan olish":
        await update.message.reply_text("Kod yuboring:")
        return MENU

    if text == "🔍 Qidirish":
        await update.message.reply_text("Kino nomini yozing:", reply_markup=cancel_markup)
        return SEARCH

    if text == "📃 Ro‘yxat":
        movies = cur.execute("SELECT code,title FROM movies").fetchall()

        if not movies:
            await update.message.reply_text("Bazadagi kino yo‘q.")
        else:
            msg = "\n".join([f"{c} — {t}" for c, t in movies])
            await update.message.reply_text(f"🎬 Kinolar:\n\n{msg}")

        return MENU

    if text == "❌ Bekor":
        return await cancel(update, context)

    # kod orqali qidirish
    movie = cur.execute(
        "SELECT title,file_id FROM movies WHERE code=?",
        (text,)
    ).fetchone()

    if movie:
        await update.message.reply_video(movie[1], caption=f"🎬 {movie[0]}")
    else:
        await update.message.reply_text("❌ Kino topilmadi")

    return MENU

# ===== SEARCH =====
async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text

    movies = cur.execute(
        "SELECT code,title FROM movies WHERE title LIKE ?",
        (f"%{name}%",)
    ).fetchall()

    if movies:
        msg = "\n".join([f"{c} — {t}" for c, t in movies])
        await update.message.reply_text(f"🔍 Natija:\n\n{msg}")
    else:
        await update.message.reply_text("Topilmadi.")

    return MENU

# ===== ADMIN ADD =====
async def add_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    await update.message.reply_text("Kod yozing:", reply_markup=cancel_markup)
    return ADD_CODE

async def add_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["code"] = update.message.text
    await update.message.reply_text("Kino nomi:")
    return ADD_TITLE

async def add_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["title"] = update.message.text
    await update.message.reply_text("Video yuboring:")
    return ADD_VIDEO

async def add_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    video = update.message.video.file_id

    cur.execute(
        "INSERT OR REPLACE INTO movies VALUES(?,?,?)",
        (context.user_data["code"],
         context.user_data["title"],
         video)
    )
    db.commit()

    await update.message.reply_text("✅ Kino saqlandi!", reply_markup=menu_markup)

    context.user_data.clear()
    return MENU

# ===== BROADCAST =====
async def broadcast_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    await update.message.reply_text("Xabar yuboring:")
    return BROADCAST

async def broadcast_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    users = cur.execute("SELECT id FROM users").fetchall()

    sent = 0
    for u in users:
        try:
            await context.bot.send_message(u[0], text)
            sent += 1
        except:
            pass

    await update.message.reply_text(f"✅ Yuborildi: {sent}")
    return MENU

# ===== CANCEL =====
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("Bekor qilindi.", reply_markup=menu_markup)
    return MENU

# ===== MAIN =====
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    user_conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, menu)],
            SEARCH: [MessageHandler(filters.TEXT, search)],
        },
        fallbacks=[MessageHandler(filters.TEXT, cancel)],
    )

    add_conv = ConversationHandler(
        entry_points=[CommandHandler("addmovie", add_movie)],
        states={
            ADD_CODE: [MessageHandler(filters.TEXT, add_code)],
            ADD_TITLE: [MessageHandler(filters.TEXT, add_title)],
            ADD_VIDEO: [MessageHandler(filters.VIDEO, add_video)],
        },
        fallbacks=[MessageHandler(filters.TEXT, cancel)],
    )

    bc_conv = ConversationHandler(
        entry_points=[CommandHandler("broadcast", broadcast_cmd)],
        states={BROADCAST: [MessageHandler(filters.TEXT, broadcast_send)]},
        fallbacks=[],
    )

    app.add_handler(user_conv)
    app.add_handler(add_conv)
    app.add_handler(bc_conv)

    print("🎬 ULTRA KINO BOT ISHLAYAPTI...")
    app.run_polling()

if __name__ == "__main__":
    main()
