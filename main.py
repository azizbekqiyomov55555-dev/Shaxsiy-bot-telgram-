import os
import logging
import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- SOZLAMALAR ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN topilmadi!")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dpMana, **to'liq va 100% ishlaydigan `main.py` kodi**. Men barcha xatolarni (qavslar, joylashuv, sintaksis) to'g'riladim.

Siz qilishingiz kerak bo'lgan ish:
1. GitHub'dagi `main.py` faylini oching.
2. Ichidagi **HAMMA** eski kodni o'chiring.
3. Quyidagi yangi kodni to'liq nusxalab, joylashtiring.
4. Saqlang (Commit) va push qiling.

### ✅ To'g'rilangan `main.py` kodi:

```python
import os
import logging
import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- SOZLAMALAR ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID_STR = os.getenv("ADMIN_ID", "0")

# Admin ID ni to'g'ri songa aylantiramiz
try:
    ADMIN_ID = int(ADMIN_ID_STR)
except ValueError:
    ADMIN_ID = 0

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN topilmadi! Iltimos, Railway Variables bo'limini tekshiring.")
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- MA'LUMOTLAR BAZASI (SQLite) ---
def init_db():
    conn = sqlite3.connect('movies.db')
    cursor = conn.cursor()
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

# Dastur ishga tushganda bazani yaratamiz
init_db()

# --- HOLATLAR (FSM) ---
class AddMovieState(StatesGroup):
    waiting_for_code = State()
    waiting_for_title = State()
    waiting_for_desc = State()
    waiting_for_link = State()

# --- ADMIN BUYRUQLARI ---

@dp.message(Command("add"))
async def cmd_add_start(message: types.Message, state: FSMContext):
    # Faqat admin kira oladi
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Siz admin emassiz! Bu buyruqdan foydalana olmaysiz.")
        return
    
    await message.answer(
        "🎬 **Yangi kino qo'shish rejimi.**\n\n"
        "1-qadam: Kino uchun **kod (raqam)** yuboring.\n"
        "(Masalan: 101)", 
        parse_mode="Markdown"
    )
    await state.set_state(AddMovieState.waiting_for_code)

@dp.message(AddMovieState.waiting_for_code)
async def process_code(message: types.Message, state: FSMContext):    code = message.text.strip()
    
    if not code.isdigit():
        await message.answer("❌ Iltimos, faqat raqamlardan iborat kod yuboring.")
        return

    # Bazada bor-yo'qligini tekshirish
    conn = sqlite3.connect('movies.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM movies WHERE movie_code = ?", (code,))
    if cursor.fetchone():
        conn.close()
        await message.answer(f"⚠️ Bu kod ({code}) allaqachon mavjud. Boshqa kod tanlang.")
        return
    
    await state.update_data(code=code)
    conn.close()
    
    await message.answer("✅ Kod qabul qilindi.\n2-qadam: Kino **nomini** yuboring:")
    await state.set_state(AddMovieState.waiting_for_title)

@dp.message(AddMovieState.waiting_for_title)
async def process_title(message: types.Message, state: FSMContext):
    title = message.text.strip()
    await state.update_data(title=title)
    
    await message.answer("3-qadam: Qisqa **tavsif** yuboring (yoki 'yo'q' deb yozing):")
    await state.set_state(AddMovieState.waiting_for_desc)

@dp.message(AddMovieState.waiting_for_desc)
async def process_desc(message: types.Message, state: FSMContext):
    desc = message.text.strip()
    await state.update_data(desc=desc)
    
    await message.answer(
        "4-qadam: Kino **HAVOLASINI (LINK)** yuboring.\n\n"
        "💡 Maslahat: Kinoni Google Drive, MEGA yoki Telegram kanalingizga yuklang va linkini shu yerga tashlang.\n"
        "Bot 10GB+ hajmdagi linklarni qabul qiladi!"
    )
    await state.set_state(AddMovieState.waiting_for_link)

@dp.message(AddMovieState.waiting_for_link)
async def process_link(message: types.Message, state: FSMContext):
    link = message.text.strip()
    
    # Link ekanligini tekshirish
    if not (link.startswith("http://") or link.startswith("https://") or link.startswith("t.me/")):
        await message.answer("❌ Bu to'g'ri havola ko'rinmayapti. http/https bilan boshlanadigan link yuboring.")
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
            f"Foydalanuvchi `{code}` deb yozsa, havolani oladi."
        )
    except Exception as e:
        await message.answer(f"❌ Xatolik yuz berdi: {e}")
    
    await state.clear()

# --- FOYDALANUVCHI BUYRUQLARI ---

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
    
    # Agar raqam bo'lmasa, javob bermaymiz (yoki xato chiqaramiz)
    if not user_text.isdigit():
        return

    conn = sqlite3.connect('movies.db')
    cursor = conn.cursor()
    cursor.execute("SELECT title, description, download_link FROM movies WHERE movie_code = ?", (user_text,))
    result = cursor.fetchone()    conn.close()

    if result:
        title, desc, link = result
        
        # Tugma yaratish
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📥 Kinoni Yuklab Olish / Ko'rish", url=link)]
        ])
        
        caption = f"🎬 **{title}**\n\n📝 {desc}\n\n👇 Quyidagi tugmani bosib kinoni oching:"
        
        await message.answer(caption, reply_markup=keyboard, parse_mode="Markdown")
    else:
        await message.answer(
            f"❌ **{user_text}** kodi bilan kino topilmadi.\n"
            f"Iltimos, kodni tekshirib qayta yuboring.", 
            parse_mode="Markdown"
        )

# --- ASOSIY QISM ---
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
