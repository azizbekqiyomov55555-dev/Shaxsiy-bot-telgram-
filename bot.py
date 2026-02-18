import asyncio
import os
from gtts import gTTS

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import CommandStart

TOKEN = "8490993231:AAEXp9bVE4DaFe47aOT8hztSUgUutw8r5Nc"

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start(msg: Message):
    await msg.answer("Matn yuboring — ovozga aylantiraman 🎤")


@dp.message(F.text)
async def text_to_voice(msg: Message):
    filename = f"{msg.from_user.id}.mp3"

    try:
        tts = gTTS(msg.text, lang="uz")
        tts.save(filename)

        with open(filename, "rb") as audio:
            await msg.answer_voice(audio)

    except Exception:
        await msg.answer("❌ Ovoz yaratib bo‘lmadi")

    finally:
        if os.path.exists(filename):
            os.remove(filename)


async def main():
    print("✅ Bot ishlayapti...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
