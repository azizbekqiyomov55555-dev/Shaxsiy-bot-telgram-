import asyncio
import os
import edge_tts

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart

TOKEN = "8312975127:AAFIXWrANgTpX_9ldK16OP97Tky3iRJqzL4"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# foydalanuvchi ovoz tanlovi
user_voice = {}

# ovoz variantlari
voices = {
    "🇺🇿 Erkak": "uz-UZ-SardorNeural",
    "🇺🇿 Ayol": "uz-UZ-MadinaNeural",
    "🇺🇸 Erkak": "en-US-GuyNeural",
    "🇺🇸 Ayol": "en-US-JennyNeural",
}

def voice_keyboard():
    buttons = [
        [InlineKeyboardButton(text=name, callback_data=code)]
        for name, code in voices.items()
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# start
@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "🎤 Ovoz tanlang:",
        reply_markup=voice_keyboard()
    )

# ovoz tanlash
@dp.callback_query()
async def choose_voice(callback: CallbackQuery):
    user_voice[callback.from_user.id] = callback.data
    await callback.message.edit_text(
        "✅ Ovoz tanlandi!\nEndi matn yuboring."
    )
    await callback.answer()

# matn → ovoz
@dp.message(F.text)
async def tts_handler(message: Message):
    voice = user_voice.get(
        message.from_user.id,
        "uz-UZ-SardorNeural"
    )

    filename = f"{message.from_user.id}.ogg"

    try:
        communicate = edge_tts.Communicate(message.text, voice)
        await communicate.save(filename)

        with open(filename, "rb") as audio:
            await message.answer_voice(audio)

    except Exception as e:
        await message.answer(f"❌ Xatolik: {e}")

    finally:
        if os.path.exists(filename):
            os.remove(filename)

# run bot
async def main():
    print("✅ Bot ishlayapti...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
