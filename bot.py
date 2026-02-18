import asyncio
import os
import random
import edge_tts

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import FSInputFile

TOKEN = "8490993231:AAEXp9bVE4DaFe47aOT8hztSUgUutw8r5Nc"

bot = Bot(TOKEN)
dp = Dispatcher()

VOICES = [
    "ja-JP-NanamiNeural",
    "en-US-JennyNeural",
    "ru-RU-DmitryNeural",
    "ko-KR-SunHiNeural",
    "fr-FR-DeniseNeural",
    "de-DE-KatjaNeural",
]

# ===== start =====
@dp.message(CommandStart())
async def start(msg: types.Message):
    await msg.answer("✅ Matn yubor")

# ===== TTS =====
@dp.message()
async def tts(msg: types.Message):

    if not msg.text:
        return

    voice = random.choice(VOICES)
    filename = f"voice_{msg.from_user.id}.mp3"

    for attempt in range(3):  # retry
        try:
            communicate = edge_tts.Communicate(msg.text, voice)
            await communicate.save(filename)

            await msg.answer_voice(FSInputFile(filename))
            os.remove(filename)
            return

        except Exception as e:
            print("Retry:", attempt, e)
            await asyncio.sleep(1)

    await msg.answer("❌ Ovoz yaratib bo‘lmadi")

# ===== run =====
async def main():
    print("✅ Bot ishga tushdi")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
