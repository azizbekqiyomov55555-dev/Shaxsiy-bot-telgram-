import asyncio
import os
import pyttsx3

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import CommandStart

TOKEN = "8490993231:AAEXp9bVE4DaFe47aOT8hztSUgUutw8r5Nc"

bot = Bot(token=TOKEN)
dp = Dispatcher()

engine = pyttsx3.init()


@dp.message(CommandStart())
async def start(msg: Message):
    await msg.answer("Matn yuboring — ovozga aylantiraman 🎤")


def make_voice(text, filename):
    engine.save_to_file(text, filename)
    engine.runAndWait()


@dp.message(F.text)
async def tts(msg: Message):
    uid = msg.from_user.id
    wav = f"{uid}.wav"

    try:
        make_voice(msg.text, wav)

        with open(wav, "rb") as audio:
            await msg.answer_voice(audio)

    except Exception as e:
        print(e)
        await msg.answer("❌ Ovoz yaratib bo‘lmadi")

    finally:
        if os.path.exists(wav):
            os.remove(wav)


async def main():
    print("✅ Bot ishlayapti")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
