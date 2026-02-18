import asyncio
import os

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import CommandStart

from gtts import gTTS
from pydub import AudioSegment

TOKEN = "8490993231:AAEXp9bVE4DaFe47aOT8hztSUgUutw8r5Nc"

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer("✅ Matn yuboring — ovozga aylantiraman 🎤")


@dp.message(F.text)
async def tts_handler(message: Message):
    user_id = message.from_user.id
    mp3_file = f"{user_id}.mp3"
    ogg_file = f"{user_id}.ogg"

    try:
        # Matn → mp3
        tts = gTTS(text=message.text, lang="uz")
        tts.save(mp3_file)

        # mp3 → ogg (telegram voice format)
        audio = AudioSegment.from_mp3(mp3_file)
        audio.export(ogg_file, format="ogg")

        # Ovoz yuborish
        with open(ogg_file, "rb") as voice:
            await message.answer_voice(voice)

    except Exception as e:
        print("XATO:", e)
        await message.answer("❌ Ovoz yaratib bo‘lmadi. Qayta urinib ko‘ring.")

    finally:
        # Fayllarni o‘chirish
        for f in [mp3_file, ogg_file]:
            if os.path.exists(f):
                os.remove(f)


async def main():
    print("✅ Bot ishga tushdi")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
