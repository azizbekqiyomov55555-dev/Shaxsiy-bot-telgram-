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

# ====== KO‘P OVOZLAR ======
VOICES = [
    "ja-JP-NanamiNeural",
    "ja-JP-KeitaNeural",
    "en-US-JennyNeural",
    "en-US-GuyNeural",
    "ru-RU-DmitryNeural",
    "ru-RU-SvetlanaNeural",
    "en-GB-SoniaNeural",
    "ko-KR-SunHiNeural",
    "fr-FR-DeniseNeural",
    "de-DE-KatjaNeural",
    "zh-CN-XiaoxiaoNeural",
    "it-IT-ElsaNeural",
]

# ====== START ======
@dp.message(CommandStart())
async def start(msg: types.Message):
    await msg.answer("✅ Matn yubor — har xil ovozda o‘qib beraman")

# ====== MATN → OVOZ ======
@dp.message()
async def tts(msg: types.Message):
    text = msg.text

    if not text:
        return

    voice = random.choice(VOICES)

    try:
        filename = f"voice_{msg.from_user.id}.mp3"

        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(filename)

        await msg.answer_voice(FSInputFile(filename))
        os.remove(filename)

    except Exception as e:
        print("XATO:", e)
        await msg.answer("❌ Ovoz yaratishda xato")

# ====== RUN ======
async def main():
    print("✅ Bot ishga tushdi")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
