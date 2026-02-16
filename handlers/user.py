from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import db
from keyboards import get_main_keyboard, get_channel_keyboard
from utils.subscription import check_subscription
import os
import logging

logger = logging.getLogger(__name__)
user_router = Router()

CHANNEL_ID = os.getenv("CHANNEL_ID")

class UserStates(StatesGroup):
    waiting_for_movie_code = State()
    waiting_for_search_query = State()

@user_router.message(F.text == "/start")
async def cmd_start(message: types.Message):
    """Start buyrug'i"""
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    
    await db.add_user(user_id, username, first_name, last_name)
    
    text = (
        f"👋 <b>Assalomu alaykum, {first_name}!</b>\n\n"
        f"🎬 <b>Kino Bot</b>ga xush kelibsiz!\n\n"
        f"Bu bot orqali eng sara kinolarni tomosha qilishingiz mumkin.\n"
        f"Kinoni ko'rish uchun quyidagi amallarni bajaring:\n\n"
        f"1️⃣ Kanalimizga obuna bo'ling\n"
        f"2️⃣ Maxsus kodni kiriting\n"
        f"3️⃣ Kinoni tomosha qiling!\n\n"
        f"📢 <b>Kanalimiz:</b> {CHANNEL_ID}"
    )
    
    await message.answer(text, reply_markup=get_main_keyboard(is_admin=False))

@user_router.message(F.text == "🎥 Kino izlash")
async def user_search_movie(message: types.Message, state: FSMContext):
    """Kino qidirish"""
    is_subscribed = await check_subscription(message.from_user.id, CHANNEL_ID)
    
    if not is_subscribed:
        await message.answer(
            "⚠️ <b>Diqqat!</b>\n\n"
            "Kinolarni ko'rish uchun avval kanalimizga obuna bo'lishingiz shart!\n\n"            "1. Quyidagi tugmani bosing\n"
            "2. Kanalga obuna bo'ling\n"
            "3. 'Obunani tekshirish' tugmasini bosing",
            reply_markup=get_channel_keyboard(CHANNEL_ID)
        )
        return
    
    await message.answer(
        "🔍 <b>Kino kodini kiriting:</b>\n\n"
        "Masalan: MATRIX, AVENGERS, SPIDERMAN\n\n"
        "🔙 Orqaga: /start"
    )
    await state.set_state(UserStates.waiting_for_movie_code)

@user_router.message(UserStates.waiting_for_movie_code)
async def user_process_movie_code(message: types.Message, state: FSMContext):
    """Kino kodini qayta ishlash"""
    is_subscribed = await check_subscription(message.from_user.id, CHANNEL_ID)
    
    if not is_subscribed:
        await message.answer(
            "⚠️ Avval kanalga obuna bo'ling!",
            reply_markup=get_channel_keyboard(CHANNEL_ID)
        )
        return
    
    code = message.text.strip().upper()
    movie = await db.get_movie(code)
    
    if movie:
        await db.update_movie_views(movie['id'])
        await db.add_movie_view(message.from_user.id, movie['id'])
        
        try:
            await message.answer_video(
                video=movie['file_id'],
                caption=f"🎬 <b>{movie['caption']}</b>\n\n"
                       f"🔑 Kod: <code>{code}</code>\n"
                       f"👁 Ko'rishlar: {movie['views'] + 1}\n\n"
                       f"📢 @{(await bot.get_me()).username}",
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Video yuborishda xatolik: {e}")
            await message.answer("❌ Video yuklashda xatolik yuz berdi. Admin bilan bog'laning.")
    else:
        await message.answer(
            f"❌ <b>{code}</b> kodi bilan kino topilmadi!\n\n"
            f"Iltimos, kodni to'g'ri yozganingizga ishonch hosil qiling yoki admin bilan bog'laning."
        )    
    await state.clear()

@user_router.message(F.text == "🔍 Qidiruv")
async def user_search_query(message: types.Message, state: FSMContext):
    """Kino qidiruv"""
    is_subscribed = await check_subscription(message.from_user.id, CHANNEL_ID)
    
    if not is_subscribed:
        await message.answer(
            "⚠️ Avval kanalga obuna bo'ling!",
            reply_markup=get_channel_keyboard(CHANNEL_ID)
        )
        return
    
    await message.answer(
        "🔍 <b>Kino nomini yozing:</b>\n\n"
        "Masalan: Matrix, Avengers, Spiderman\n\n"
        "🔙 Orqaga: /start"
    )
    await state.set_state(UserStates.waiting_for_search_query)

@user_router.message(UserStates.waiting_for_search_query)
async def user_process_search_query(message: types.Message, state: FSMContext):
    """Qidiruv natijalari"""
    query = message.text.strip()
    movies = await db.search_movies(query)
    
    if not movies:
        await message.answer(f"❌ <b>{query}</b> bo'yicha hech narsa topilmadi!")
        await state.clear()
        return
    
    text = f"🔍 <b>Qidiruv natijalari ({len(movies)} ta):</b>\n\n"
    for i, movie in enumerate(movies[:10], 1):
        text += f"{i}. <code>{movie['code']}</code> - {movie['caption']}\n"
    
    await message.answer(text)
    await state.clear()

@user_router.message(F.text == "📢 Kanalimiz")
async def user_channel(message: types.Message):
    """Kanal haqida"""
    await message.answer(
        f"📢 <b>Bizning kanalimiz:</b>\n\n"
        f"{CHANNEL_ID}\n\n"
        f"Eng yangi kinolar va yangiliklar uchun obuna bo'ling!",
        reply_markup=get_channel_keyboard(CHANNEL_ID)
    )
@user_router.message(F.text == "📞 Aloqa")
async def user_contact(message: types.Message):
    """Aloqa"""
    await message.answer(
        "📞 <b>Aloqa:</b>\n\n"
        "Savollar yoki takliflar uchun:\n"
        f"@{(await bot.get_me()).username} adminiga yozing."
    )

@user_router.callback_query(F.data == "check_subscription")
async def callback_check_sub(callback: types.CallbackQuery):
    """Obunani tekshirish"""
    is_subscribed = await check_subscription(callback.from_user.id, CHANNEL_ID)
    
    if is_subscribed:
        await callback.message.edit_text(
            "✅ <b>Tabriklaymiz!</b>\n\n"
            "Obuna muvaffaqiyatli amalga oshirildi.\n"
            "Endi kinolarni ko'rishingiz mumkin!",
            reply_markup=get_main_keyboard(is_admin=False)
        )
    else:
        await callback.answer("⚠️ Hali obuna bo'lmadingiz!", show_alert=True)

@user_router.callback_query(F.data == "back_to_menu")
async def callback_back_menu(callback: types.CallbackQuery):
    """Menyuga qaytish"""
    await callback.message.edit_text(
        "🎬 <b>Kino Bot</b>\n\n"
        "Menyuni tanlang:",
        reply_markup=get_main_keyboard(is_admin=False)
)
