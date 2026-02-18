import asyncio
import os
import edge_tts

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile

TOKEN = "8490993231:AAEXp9bVE4DaFe47aOT8hztSUgUutw8r5Nc"

bot = Bot(TOKEN)
dp = Dispatcher()

# ====== OVOZLAR ======
VOICES = {
    "Anime qiz 🇯🇵": "ja-JP-NanamiNeural",
    "Anime yigit 🇯🇵": "ja-JP-KeitaNeural",
    "Multik qiz 🇺🇸": "en-US-JennyNeural",
    "Multik yigit 🇺🇸": "en-US-GuyNeural",
    "Robot 🤖": "en-US-AriaNeural",
    "Rus erkak 🇷🇺": "ru-RU-DmitryNeural",
    "Rus ayol 🇷🇺": "ru-RU-SvetlanaNeural",
    "Britan qiz 🇬🇧": "en-GB-SoniaNeural",
    "Koreys 🇰🇷": "ko-KR-SunHiNeural",
    "Xitoy 🇨🇳": "zh-CN-XiaoxiaoNeural",
    "Fransuz 🇫🇷": "fr-FR-DeniseNeural",
    "Nemis 🇩🇪": "de-DE-KatjaNeural",
}

user_voice = {}

# ====== TUGMALAR ======
def voice_menu():
    buttons = [
        [InlineKeyboardButton(text=name, callback_data=name)]
        for name in VOICES
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# ====== START ======
@dp.message(CommandStart())
async def start(msg: types.Message):
    await msg.answer(
        "🎤 Ovoz tanlang:",
        reply_markup=voice_menu()
    )

# ====== OVOZ TANLASH ======
@dp.callback_query(F.data.in_(VOICES.keys()))
async def choose_voice(call: types.CallbackQuery):
    user_voice[call.from_user.id] = VOICES[call.data]

    await call.message.answer(
        f"✅ Tanlandi: {call.data}\nEndi matn yubor!"
    )
    await call.answer()

# ====== MATN → OVOZ ======
@dp.message()
async def tts(msg: types.Message):
    voice = user_voice.get(msg.from_user.id)

    if not voice:
        await msg.answer("⚠️ Avval ovoz tanlang /start")
        return

    text = msg.text

    try:
        filename = f"voice_{msg.from_user.id}.mp3"

        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(filename)

        await msg.answer_voice(FSInputFile(filename))
        os.remove(filename)

    except Exception as e:
        print("XATO:", e)
        await msg.answer("❌ Ovoz yaratishda xato")

# ====== RUN ======
async def main():
    print("✅ Bot ishga tushdi")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
