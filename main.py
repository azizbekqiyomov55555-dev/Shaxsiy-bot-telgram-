import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

# ================== TOKEN ==================
BOT_TOKEN = "TOKENINGNI_BU_YERGA_QO'Y"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ================== DATABASE ==================
def init_db():
    conn = sqlite3.connect("movies.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            movie_code TEXT UNIQUE,
            title TEXT,
            description TEXT,
            download_link TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ================== ADMIN HOLATLAR ==================
class AddMovie(StatesGroup):
    code = State()
    title = State()
    desc = State()
    link = State()

ADMIN_ID = 123456789  # O'zingni Telegram ID'ingni yoz

# ================== ADMIN BUYRUQLARI ==================

@dp.message(Command("add"))
async def add_movie_start(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("❌ Siz admin emassiz.")
    
    await message.answer("🎬 Kino kodini yuboring:")
    await state.set_state(AddMovie.code)

@dp.message(AddMovie.code)
async def get_code(message: types.Message, state: FSMContext):
    await state.update_data(code=message.text.strip())
    await message.answer("🎬 Kino nomini yuboring:")
    await state.set_state(AddMovie.title)

@dp.message(AddMovie.title)
async def get_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text.strip())
    await message.answer("📝 Kino haqida qisqa tavsif yuboring:")
    await state.set_state(AddMovie.desc)

@dp.message(AddMovie.desc)
async def get_desc(message: types.Message, state: FSMContext):
    await state.update_data(desc=message.text.strip())
    await message.answer("🔗 Yuklab olish havolasini yuboring (http/https bilan):")
    await state.set_state(AddMovie.link)

@dp.message(AddMovie.link)
async def get_link(message: types.Message, state: FSMContext):
    link = message.text.strip()

    if not link.startswith("http"):
        await message.answer("❌ To'g'ri link yuboring (http/https bilan).")
        return

    data = await state.get_data()
    code = data["code"]
    title = data["title"]
    desc = data["desc"]

    try:
        conn = sqlite3.connect("movies.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO movies (movie_code, title, description, download_link) VALUES (?, ?, ?, ?)",
            (code, title, desc, link)
        )
        conn.commit()
        conn.close()

        await message.answer(
            f"✅ Kino muvaffaqiyatli qo'shildi!\n\n"
            f"🎬 Nomi: {title}\n"
            f"🔢 Kodi: {code}\n"
            f"Foydalanuvchi {code} deb yozsa, havolani oladi."
        )

    except Exception as e:
        await message.answer(f"❌ Xatolik: {e}")

    await state.clear()

# ================== FOYDALANUVCHI BUYRUQLARI ==================

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    text = (
        "🍿 Kino Botiga Xush Kelibsiz!\n\n"
        "Kinoni ko'rish uchun uning kodini yuboring.\n\n"
        "Masalan: 101"
    )
    await message.answer(text)

@dp.message(F.text)
async def handle_movie_request(message: types.Message):
    user_text = message.text.strip()

    if not user_text.isdigit():
        return

    conn = sqlite3.connect("movies.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT title, description, download_link FROM movies WHERE movie_code = ?",
        (user_text,)
    )
    result = cursor.fetchone()
    conn.close()

    if result:
        title, desc, link = result

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="📥 Kinoni Ko'rish / Yuklab Olish", url=link)]
            ]
        )

        caption = f"🎬 {title}\n\n📝 {desc}"

        await message.answer(caption, reply_markup=keyboard)

    else:
        await message.answer("❌ Bunday kodli kino topilmadi.")

# ================== MAIN ==================

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
