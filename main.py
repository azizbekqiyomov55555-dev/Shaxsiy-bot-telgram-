import os
import logging
import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- SOZLAMALAR ---
BOT_TOKEN = "8356052924:AAG0auwyE4QSXLqI6adK8CUOfwzd7DWnihY"
ADMIN_ID = "8332077004"

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN topilmadi!")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- MA'LUMOTLAR BAZASI ---
def init_db():
    conn = sqlite3.connect('movies.db')
    cursor = conn.cursor()
    # Endi file_id emas, link saqlaymiz
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            movie_code TEXT UNIQUE,
            title TEXT,
            description TEXT,
            download_link TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- HOLATLAR ---
class AddMovieState(StatesGroup):
    waiting_for_code = State()
    waiting_for_title = State()
    waiting_for_desc = State()
    waiting_for_link = State()

# --- ADMIN QISMI ---

@dp.message(Command("add"))
async def cmd_add_start(message: types.Message, state: FSMContext):    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Siz admin emassiz!")
        return
    
    await message.answer("🎬 **Yangi kino qo'shish (10GB+ qo'llab-quvvatlanadi)**\n\n1-qadam: Kino uchun **kod (raqam)** yuboring.\n(Masalan: 101)")
    await state.set_state(AddMovieState.waiting_for_code)

@dp.message(AddMovieState.waiting_for_code)
async def process_code(message: types.Message, state: FSMContext):
    code = message.text.strip()
    if not code.isdigit():
        await message.answer("❌ Faqat raqam kiriting.")
        return

    conn = sqlite3.connect('movies.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM movies WHERE movie_code = ?", (code,))
    if cursor.fetchone():
        conn.close()
        await message.answer(f"⚠️ Kod {code} allaqachon mavjud!")
        return
    
    await state.update_data(code=code)
    conn.close()
    
    await message.answer("✅ Kod qabul qilindi.\n2-qadam: Kino **nomini** yuboring:")
    await state.set_state(AddMovieState.waiting_for_title)

@dp.message(AddMovieState.waiting_for_title)
async def process_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text.strip())
    await message.answer("3-qadam: Qisqa **tavsif** (syujet) yuboring (yoki 'yo'q' deb yuboring):")
    await state.set_state(AddMovieState.waiting_for_desc)

@dp.message(AddMovieState.waiting_for_desc)
async def process_desc(message: types.Message, state: FSMContext):
    await state.update_data(desc=message.text.strip())
    await message.answer(
        "4-qadam: Kino **HAVOLASINI (LINK)** yuboring.\n\n"
        "💡 Maslahat: Kinoni Google Drive, MEGA yoki Telegram kanalingizga yuklang va shu yerdan linkni olib shu yerga tashlang.\n"
        "Bot 10GB, 20GB har qanday hajmdagi linkni qabul qiladi!"
    )
    await state.set_state(AddMovieState.waiting_for_link)

@dp.message(AddMovieState.waiting_for_link)
async def process_link(message: types.Message, state: FSMContext):
    link = message.text.strip()
    
    # Link ekanligini oddiy tekshirish
    if not (link.startswith("http://") or link.startswith("https://") or link.startswith("t.me/")):        await message.answer("❌ Bu to'g'ri havola ko'rinmayapti. Iltimos, http/https bilan boshlanadigan link yuboring.")
        return

    data = await state.get_data()
    code = data['code']
    title = data['title']
    desc = data['desc']

    try:
        conn = sqlite3.connect('movies.db')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO movies (movie_code, title, description, download_link) VALUES (?, ?, ?, ?)", 
            (code, title, desc, link)
        )
        conn.commit()
        conn.close()
        
        await message.answer(
            f"✅ **Kino muvaffaqiyatli qo'shildi!**\n\n"
            f"🎬 Nomi: {title}\n"
            f"🔢 Kodi: {code}\n"
            f"📏 Hajmi: Cheklovsiz (Link orqali)\n\n"
            f"Foydalanuvchi `{code}` deb yozsa, havolani oladi."
        )
    except Exception as e:
        await message.answer(f"❌ Xatolik: {e}")
    
    await state.clear()

# --- FOYDALANUVCHI QISMI ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    text = (
        "🍿 **Kino Olami Botiga Xush Kelibsiz!**\n\n"
        "Bizda eng so'nggi va og'ir vaznli (4K, 10GB+) kinolar bor.\n"
        "Kinoni ko'rish uchun uning **kodini** yuboring.\n\n"
        "Masalan: `101`, `205`"
    )
    await message.answer(text, parse_mode="Markdown")

@dp.message(F.text)
async def handle_movie_request(message: types.Message):
    user_text = message.text.strip()
    
    if not user_text.isdigit():
        # Agar raqam bo'lmasa va buyruq bo'lmasa, javob bermaslik mumkin
        return
    conn = sqlite3.connect('movies.db')
    cursor = conn.cursor()
    cursor.execute("SELECT title, description, download_link FROM movies WHERE movie_code = ?", (user_text,))
    result = cursor.fetchone()
    conn.close()

    if result:
        title, desc, link = result
        
        # Tugma yaratish
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📥 Kinoni Yuklab Olish / Ko'rish", url=link)]
        ])
        
        caption = f"🎬 **{title}**\n\n📝 {desc}\n\n👇 Quyidagi tugmani bosib kinoni oching:"
        
        await message.answer(caption, reply_markup=keyboard, parse_mode="Markdown")
    else:
        await message.answer(f"❌ **{user_text}** kodi bilan kino topilmadi.\nKodni tekshirib qayta yuboring.", parse_mode="Markdown")

# --- ISHGA TUSHIRISH ---
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
