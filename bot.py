import asyncio
import os
import edge_tts

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart

TOKEN = "8490993231:AAEXp9bVE4DaFe47aOT8hztSUgUutw8r5Nc"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# foydalanuvchi ovoz tanlovi
user_voice = {}

# 12 ta ovoz
voices = {
    "🇺🇿 Erkak 1": "uz-UZ-SardorNeural",
    "🇺🇿 Ayol 1": "uz-UZ-MadinaNeural",
    "🇺🇸 Erkak": "en-US-GuyNeural",
    "🇺🇸 Ayol": "en-US-JennyNeural",
    "🇬🇧 Erkak": "en-GB-RyanNeural",
    "🇬🇧 Ayol": "en-GB-SoniaNeural",
    "🇷🇺 Erkak": "ru-RU-DmitryNeural",
    "🇷🇺 Ayol": "ru-RU-SvetlanaNeural",
    "🇹🇷 Erkak": "tr-TR-AhmetNeural",
    "🇹🇷 Ayol": "tr-TR-EmelNeural",
    "🇩🇪 Erkak": "de-DE-ConradNeural",
    "🇩🇪 Ayol": "de-DE-KatjaNeural",
}

def voice_keyboard():
    buttons = []
    temp = []

    for name, code in voices.items():
        temp.append(InlineKeyboardButton(text=name, callback_data=code))
        if len(temp) == 2:
            buttons.append(temp)
            temp = []

    if temp:
        buttons.append(temp)

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
    voice = user_voice.get(message.from_user.id, "uz-UZ-SardorNeural")
    filename = f"{message.from_user.id}.ogg"

    try:
        success = False

        for _ in range(3):  # retry
            try:
                communicate = edge_tts.Communicate(message.text, voice)
                await communicate.save(filename)
                success = True
                break
            except:
                await asyncio.sleep(1)

        if not success:
            raise Exception("TTS server band")

        with open(filename, "rb") as audio:
            await message.answer_voice(audio)

    except Exception as e:
        await message.answer("❌ Ovoz yaratib bo‘lmadi. Qayta urinib ko‘ring.")

    finally:
        if os.path.exists(filename):
            os.remove(filename)

# run
async def main():
    print("✅ Bot ishlayapti...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
