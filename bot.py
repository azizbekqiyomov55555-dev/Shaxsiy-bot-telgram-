import asyncio
import os
from gtts import gTTS

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import FSInputFile

TOKEN = "8490993231:AAEXp9bVE4DaFe47aOT8hztSUgUutw8r5Nc"

bot = Bot(TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start(msg: types.Message):
    await msg.answer("✅ Matn yubor — ovozga aylantiraman")

@dp.message()
async def tts(msg: types.Message):

    if not msg.text:
        return

    try:
        filename = f"voice_{msg.from_user.id}.mp3"

        tts = gTTS(text=msg.text, lang="ru")
        tts.save(filename)

        await msg.answer_voice(FSInputFile(filename))
        os.remove(filename)

    except Exception as e:
        print(e)
        await msg.answer("❌ Ovoz yaratib bo‘lmadi")

async def main():
    print("✅ Bot ishga tushdi")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
