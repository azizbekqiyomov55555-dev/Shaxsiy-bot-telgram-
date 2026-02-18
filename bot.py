import asyncio
import os
import edge_tts

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import CommandStart

TOKEN = "8490993231:AAEXp9bVE4DaFe47aOT8hztSUgUutw8r5Nc"

VOICE = "uz-UZ-SardorNeural"  # o'zbek ovoz

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start(msg: Message):
    await msg.answer("Matn yuboring — ovozga aylantiraman 🎤")


@dp.message(F.text)
async def tts(msg: Message):
    file = f"{msg.from_user.id}.ogg"

    try:
        communicate = edge_tts.Communicate(msg.text, VOICE)
        await communicate.save(file)

        with open(file, "rb") as audio:
            await msg.answer_voice(audio)

    except Exception as e:
        print(e)
        await msg.answer("❌ Ovoz yaratib bo‘lmadi")

    finally:
        if os.path.exists(file):
            os.remove(file)


async def main():
    print("✅ Bot ishlayapti")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
