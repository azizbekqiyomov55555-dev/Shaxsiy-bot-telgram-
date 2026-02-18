import asyncio
import os
import edge_tts

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart

TOKEN = "8490993231:AAEXp9bVE4DaFe47aOT8hztSUgUutw8r5Nc"

bot = Bot(token=TOKEN)
dp = Dispatcher()

user_voice = {}

voices = {
    "🎈 Multik qiz": "en-US-AnaNeural",
    "🤖 Robot": "en-US-GuyNeural",
    "👧 Anime": "ja-JP-NanamiNeural",
    "🧒 Multik bola": "en-GB-RyanNeural",
    "👩 Ayol": "ru-RU-SvetlanaNeural",
    "👨 Erkak": "ru-RU-DmitryNeural",
    "⚡ Tez": "en-US-JennyNeural",
    "🐢 Sekin": "de-DE-KatjaNeural",
    "🎤 Normal": "en-US-AriaNeural",
    "🎭 Multik effekt": "ko-KR-SunHiNeural",
}

def keyboard():
    rows = []
    row = []
    for name, voice in voices.items():
        row.append(InlineKeyboardButton(text=name, callback_data=voice))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    return InlineKeyboardMarkup(inline_keyboard=rows)

@dp.message(CommandStart())
async def start(msg: Message):
    await msg.answer("🎭 Ovoz tanlang:", reply_markup=keyboard())

@dp.callback_query()
async def choose(cb: CallbackQuery):
    user_voice[cb.from_user.id] = cb.data
    await cb.message.edit_text("✅ Tanlandi! Endi matn yuboring.")
    await cb.answer()

@dp.message(F.text)
async def tts(msg: Message):
    voice = user_voice.get(msg.from_user.id, "en-US-AriaNeural")
    file = f"{msg.from_user.id}.mp3"

    try:
        communicate = edge_tts.Communicate(msg.text, voice)
        await communicate.save(file)

        with open(file, "rb") as audio:
            await msg.answer_voice(audio)

    except:
        await msg.answer("❌ Ovoz yaratib bo‘lmadi.")

    finally:
        if os.path.exists(file):
            os.remove(file)

async def main():
    print("✅ Bot ishlayapti")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
