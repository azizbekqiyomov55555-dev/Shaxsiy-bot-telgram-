import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
import edge_tts
import os

TOKEN = "8490993231:AAEXp9bVE4DaFe47aOT8hztSUgUutw8r5Nc"

bot = Bot(TOKEN)
dp = Dispatcher()

VOICE = "ru-RU-DmitryNeural"  # Railway ishlaydigan ovoz

@dp.message(CommandStart())
async def start(msg: types.Message):
    await msg.answer("✅ Matn yubor — ovozga aylantiraman")

@dp.message()
async def tts(msg: types.Message):
    text = msg.text

    try:
        file = f"voice_{msg.from_user.id}.mp3"

        communicate = edge_tts.Communicate(text, VOICE)
        await communicate.save(file)

        await msg.answer_voice(types.FSInputFile(file))
        os.remove(file)

    except Exception as e:
        print("XATO:", e)
        await msg.answer("❌ Ovoz yaratib bo‘lmadi")

async def main():
    print("✅ Bot ishga tushdi")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
