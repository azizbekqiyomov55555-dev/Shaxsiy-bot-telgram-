import asyncio
import os

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart

from gtts import gTTS
from pydub import AudioSegment

TOKEN = "8490993231:AAEXp9bVE4DaFe47aOT8hztSUgUutw8r5Nc"

bot = Bot(token=TOKEN)
dp = Dispatcher()

user_style = {}

styles = {
    "🎈 Multik": 1.3,
    "🐿 Chipmunk": 1.6,
    "🐢 Sekin": 0.8,
    "🎤 Normal": 1.0,
    "🤖 Robot": 0.6,
    "⚡ Tez": 1.2,
}

def keyboard():
    buttons = []
    row = []
    for name, speed in styles.items():
        row.append(InlineKeyboardButton(text=name, callback_data=str(speed)))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@dp.message(CommandStart())
async def start(msg: Message):
    await msg.answer("🎭 Ovoz uslubini tanlang:", reply_markup=keyboard())

@dp.callback_query()
async def choose(cb: CallbackQuery):
    user_style[cb.from_user.id] = float(cb.data)
    await cb.message.edit_text("✅ Tanlandi! Endi matn yuboring.")
    await cb.answer()

def change_speed(sound, speed):
    altered = sound._spawn(sound.raw_data, overrides={
        "frame_rate": int(sound.frame_rate * speed)
    })
    return altered.set_frame_rate(44100)

@dp.message(F.text)
async def tts(msg: Message):
    speed = user_style.get(msg.from_user.id, 1.0)

    try:
        mp3 = f"{msg.from_user.id}.mp3"
        ogg = f"{msg.from_user.id}.ogg"

        tts = gTTS(msg.text, lang="uz")
        tts.save(mp3)

        sound = AudioSegment.from_mp3(mp3)
        sound = change_speed(sound, speed)
        sound.export(ogg, format="ogg")

        with open(ogg, "rb") as v:
            await msg.answer_voice(v)

    except Exception as e:
        await msg.answer("❌ Ovoz yaratib bo‘lmadi.")

    finally:
        for f in [mp3, ogg]:
            if os.path.exists(f):
                os.remove(f)

async def main():
    print("✅ Bot ishlayapti")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
