import asyncio
import os

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from gtts import gTTS

TOKEN = "8490993231:AAEXp9bVE4DaFe47aOT8hztSUgUutw8r5Nc"

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("✅ Matn yubor — ovozga aylantiraman 🎤")


@dp.message(F.text)
async def tts(message: Message):
    try:
        filename = f"{message.from_user.id}.mp3"

        tts = gTTS(message.text, lang="uz")
        tts.save(filename)

        with open(filename, "rb") as audio:
            await message.answer_audio(audio)

        os.remove(filename)

    except Exception as e:
        print(e)
        await message.answer("❌ Xatolik. Internet yoki servis muammosi.")


async def main():
    print("✅ Bot ishga tushdi")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
