import asyncio
import os
import subprocess

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import CommandStart

TOKEN = "8490993231:AAEXp9bVE4DaFe47aOT8hztSUgUutw8r5Nc"

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("✅ Matn yubor — ovozga aylantiraman 🎤")


@dp.message(F.text)
async def tts(message: Message):
    user_id = message.from_user.id
    wav_file = f"{user_id}.wav"
    ogg_file = f"{user_id}.ogg"

    try:
        # matn → wav (offline)
        subprocess.run([
            "espeak",
            "-v", "tr",   # turk ovozi (uzbekka yaqin)
            "-w", wav_file,
            message.text
        ])

        # wav → ogg (telegram voice)
        subprocess.run([
            "ffmpeg",
            "-i", wav_file,
            ogg_file,
            "-y"
        ])

        with open(ogg_file, "rb") as f:
            await message.answer_voice(f)

    except Exception as e:
        print(e)
        await message.answer("❌ Xatolik yuz berdi")

    finally:
        for f in [wav_file, ogg_file]:
            if os.path.exists(f):
                os.remove(f)


async def main():
    print("✅ Bot ishlayapti")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
