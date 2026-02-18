import asyncio
import os
import edge_tts

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart

TOKEN = "BOT_TOKENNI_BU_YERGA"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# foydalanuvchi ovoz tanlovi
user_voice = {}

# ovoz variantlari
voices = {
    "Erkak 🇺🇿": "uz-UZ-SardorNeural",
    "Ayol 🇺🇿": "uz-UZ-MadinaNeural",
    "Erkak 🇺🇸": "en-US-GuyNeural",
    "Ayol 🇺🇸": "en-US-JennyNeural",
}

def voice_keyboard():
    buttons = [
        [InlineKeyboardButton(text=name, callback_data=code)]
        for name, code in voices.items()
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "🎤 Ovoz tanlang:",
        reply_markup=voice_keyboard()
    )

@dp.callback_query()
async def choose_voice(callback):
    user_voice[callback.from_user.id] = callback.data
    await callback.message.edit_text("✅ Ovoz tanlandi!\nEndi matn yuboring.")

@dp.message(F.text)
async def tts_handler(message: Message):
    voice = user_voice.get(message.from_user.id, "uz-UZ-SardorNeural")

    filename = f"{message.from_user.id}.mp3"

    communicate = edge_tts.Communicate(message.text, voice)
    await communicate.save(filename)

    await message.answer_voice(open(filename, "rb"))

    os.remove(filename)

async def main():
    print("✅ Bot ishlayapti...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
