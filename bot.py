import asyncio
import os
import edge_tts
from gtts import gTTS

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import CommandStart

TOKEN = "8490993231:AAEXp9bVE4DaFe47aOT8hztSUgUutw8r5Nc"
VOICE = "uz-UZ-SardorNeural"

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start(msg: Message):
    await msg.answer("Matn yuboring — ovozga aylantiraman 🎤")


@dp.message(F.text)
async def tts(msg: Message):
    uid = msg.from_user.id
    edge_file = f"{uid}_edge.ogg"
    gtts_file = f"{uid}_gtts.mp3"

    # ===== TRY EDGE =====
    try:
        communicate = edge_tts.Communicate(msg.text, VOICE)
        await communicate.save(edge_file)

        with open(edge_file, "rb") as audio:
            await msg.answer_voice(audio)

        os.remove(edge_file)
        return

    except Exception as e:
        print("EDGE FAILED:", e)

    # ===== FALLBACK gTTS =====
    try:
        tts = gTTS(msg.text, lang="uz")
        tts.save(gtts_file)

        with open(gtts_file, "rb") as audio:
            await msg.answer_voice(audio)

        os.remove(gtts_file)

    except Exception as e:
        print("GTTS FAILED:", e)
        await msg.answer("❌ Ovoz servisiga ulanib bo‘lmadi. Keyinroq urinib ko‘ring.")


async def main():
    print("✅ Bot ishlayapti")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
