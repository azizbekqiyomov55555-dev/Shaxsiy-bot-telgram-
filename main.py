import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

# Sozlamalarni yuklash
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
CHANNEL_ID = os.getenv("CHANNEL_ID")

# Log sozlamalari
logging.basicConfig(level=logging.INFO)

# Bot va Dispatcher yaratish
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Ma'lumotlar bazasi (Xotirada saqlanadi - Restart bo'lsa o'chadi. 
# Haqiqiy loyihada SQLite yoki PostgreSQL ishlatish kerak)
movies_db = {}  # Format: {'kod': {'file_id': ..., 'caption': ...}}

# Holatlar (FSM)
class AdminState(StatesGroup):
    waiting_for_code = State()
    waiting_for_movie = State()

class UserState(StatesGroup):
    waiting_for_code_input = State()

# --- YORDAMCHI FUNKSIYALAR ---

async def check_subscription(user_id: int) -> bool:
    """Foydalanuvchi kanalga obuna bo'lganligini tekshiradi"""
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logging.error(f"Obunani tekshirishda xatolik: {e}")
        return False

def get_start_keyboard():
    """Start tugmasi uchun klaviatura"""
    kb = [
        [KeyboardButton(text="🎬 Kinolarni ko'rish", callback_data="show_movies")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_channel_keyboard():
    """Majburiy obuna uchun tugma"""
    kb = [
        [InlineKeyboardButton(text="📢 Kanalga obuna bo'lish", url=f"https://t.me/{CHANNEL_ID.replace('@', '')}"),
         InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_sub")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

# --- HANDLERLAR (BUYRUQLAR) ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        text = "Assalomu alaykum, Hurmatli Admin! 👋\nBot boshqaruv paneliga xush kelibsiz."
        kb = [
            [KeyboardButton(text="➕ Yangi kino qo'shish", callback_data="add_movie")],
            [KeyboardButton(text="📊 Statistika", callback_data="stats")]
        ]
        await message.answer(text, reply_markup=ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True))
    else:
        await message.answer("Assalomu alaykum! 🎬\nEng zo'r kinolarni tomosha qilish uchun quyidagi tugmani bosing.", reply_markup=get_start_keyboard())

@dp.callback_query(F.data == "show_movies")
async def show_movies_menu(callback: types.CallbackQuery):
    # Obunani tekshirish
    if not await check_subscription(callback.from_user.id):
Salom! Siz so'ragan **Kino Bot** loyihasi uchun to'liq kodni tayyorlab beraman. Bu bot quyidagi funksiyalarga ega bo'ladi:

1.  **Start:** "Assalomu alaykum" deb javob beradi.
2.  **Majburiy obuna:** Foydalanuvchi kanalda yo'q bo'lsa, kinoni ko'ra olmaydi va "Obuna bo'ling" tugmasi chiqadi.
3.  **Admin paneli:** Admin kinoni yuklaydi va unga maxsus **kod** biriktiradi.
4.  **Foydalanuvchi:** Kodni yozganda kino chiqadi.

Ushbu loyihani GitHub ga yuklash va Railway da ishga tushirish uchun eng qulay kutubxona — **aiogram (3.x versiyasi)** dan foydalanamiz.

### 1. Loyiha tuzilishi (Papka ichida shunday bo'lishi kerak)

Kompyuteringizda yangi papka oching (masalan, `kino_bot`) va ichiga quyidagi fayllarni yarating:

```text
kino_bot/
├── .env                # Maxfiy kalitlar (Token, ID lar)
├── main.py             # Asosiy bot kodi
├── requirements.txt    # Kerakli kutubxonalar ro'yxati
└── README.md           # Tushuntirish (ixtiyoriy)
