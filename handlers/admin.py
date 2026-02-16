from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import State, StatesGroup
from database import db
from keyboards import get_main_keyboard, get_admin_movie_list_keyboard, get_confirmation_keyboard
from filters import IsAdminFilter
import logging

logger = logging.getLogger(__name__)
admin_router = Router()

class AdminStates(StatesGroup):
    waiting_for_movie_code = State()
    waiting_for_movie_file = State()
    waiting_for_movie_caption = State()
    waiting_for_delete_code = State()
    waiting_for_broadcast_message = State()
    waiting_for_welcome_text = State()

@admin_router.message(Command("admin"), IsAdminFilter())
async def cmd_admin(message: types.Message):
    """Admin panelni ochish"""
    stats = await db.get_full_statistics()
    text = (
        f"👤 <b>Admin Panel</b>\n\n"
        f"📊 <b>Statistika:</b>\n"
        f"• Foydalanuvchilar: {stats['users_count']}\n"
        f"• Kinolar: {stats['movies_count']}\n"
        f"• Jami ko'rishlar: {stats['total_views']}\n"
        f"• Bugungi ko'rishlar: {stats['today_views']}\n\n"
        f"🛠 <b>Amallarni tanlang:</b>"
    )
    await message.answer(text, reply_markup=get_main_keyboard(is_admin=True))

@admin_router.message(F.text == "🎬 Yangi kino qo'shish", IsAdminFilter())
async def admin_add_movie_start(message: types.Message, state: FSMContext):
    """Kino qo'shishni boshlash"""
    await message.answer(
        "🔢 <b>Yangi kino uchun KOD kiriting:</b>\n\n"
        "• Lotin harflari va raqamlardan foydalaning\n"
        "• Masalan: MATRIX2024, AVENGERS, SPIDERMAN\n"
        "• Kod 3-20 belgidan iborat bo'lishi kerak\n\n"
        "❌ Bekor qilish: /cancel"
    )
    await state.set_state(AdminStates.waiting_for_movie_code)

@admin_router.message(AdminStates.waiting_for_movie_code, IsAdminFilter())
async def admin_process_code(message: types.Message, state: FSMContext):
    """Kodni qabul qilish"""    code = message.text.strip().upper()
    
    if len(code) < 3 or len(code) > 20:
        await message.answer("❌ Kod 3-20 belgi oralig'ida bo'lishi kerak! Qayta kiriting:")
        return
    
    existing = await db.get_movie(code)
    if existing:
        await message.answer(f"⚠️ Bu kod (<b>{code}</b>) allaqachon mavjud! Boshqa kod kiriting:")
        return
    
    await state.update_data(movie_code=code)
    await message.answer(
        "✅ Kod qabul qilindi!\n\n"
        "🎬 Endi <b>kino faylini</b> yuboring:\n"
        "• Video formatida bo'lishi kerak\n"
        "• Maksimum 2GB\n"
        "• Fayl sifatida yuboring (link emas)\n\n"
        "❌ Bekor qilish: /cancel"
    )
    await state.set_state(AdminStates.waiting_for_movie_file)

@admin_router.message(AdminStates.waiting_for_movie_file, F.video, IsAdminFilter())
async def admin_process_video(message: types.Video, state: FSMContext):
    """Videoni qabul qilish"""
    data = await state.get_data()
    code = data['movie_code']
    file_id = message.video.file_id
    
    await state.update_data(movie_file_id=file_id)
    await message.answer(
        "📝 <b>Izoh yozing (ixtiyoriy):</b>\n\n"
        "• Kino nomi, yili, janri\n"
        "• Masalan: Matrix (1999) - Fantastika\n\n"
        "⏭ O'tkazib yuborish: /skip"
    )
    await state.set_state(AdminStates.waiting_for_movie_caption)

@admin_router.message(AdminStates.waiting_for_movie_file, IsAdminFilter())
async def admin_wrong_file_type(message: types.Message):
    """Noto'g'ri fayl turi"""
    await message.answer("❌ Iltimos, faqat <b>video fayl</b> yuboring! Qayta urinib ko'ring:")

@admin_router.message(AdminStates.waiting_for_movie_caption, IsAdminFilter())
async def admin_process_caption(message: types.Message, state: FSMContext):
    """Izohni qabul qilish"""
    data = await state.get_data()
    code = data['movie_code']
    file_id = data['movie_file_id']
    caption = message.text if message.text != "/skip" else ""    
    success = await db.add_movie(code, file_id, 'video', caption)
    
    if success:
        await message.answer(
            f"✅ <b>Muvaffaqiyatli qo'shildi!</b>\n\n"
            f"🎬 Kod: <code>{code}</code>\n"
            f"📝 Izoh: {caption if caption else 'Yo'q'}\n\n"
            f"Foydalanuvchilar shu kodni yozganda kino chiqadi.",
            reply_markup=get_main_keyboard(is_admin=True)
        )
    else:
        await message.answer("❌ Xatolik yuz berdi! Qayta urinib ko'ring.")
    
    await state.clear()

@admin_router.message(F.text == "📋 Kinolar ro'yxati", IsAdminFilter())
async def admin_movie_list(message: types.Message):
    """Kinolar ro'yxatini ko'rsatish"""
    movies = await db.get_all_movies()
    
    if not movies:
        await message.answer("📭 Hozircha kinolar yo'q.")
        return
    
    text = f"📋 <b>Barcha kinolar ({len(movies)} ta):</b>\n\n"
    for i, movie in enumerate(movies[:20], 1):
        text += f"{i}. <code>{movie['code']}</code> - 👁 {movie['views']}\n"
    
    if len(movies) > 20:
        text += f"\n... va yana {len(movies) - 20} ta kino"
    
    await message.answer(text, reply_markup=get_admin_movie_list_keyboard(movies))

@admin_router.message(F.text == "🗑 Kinoni o'chirish", IsAdminFilter())
async def admin_delete_movie_start(message: types.Message, state: FSMContext):
    """Kinoni o'chirish"""
    await message.answer(
        "🗑 <b>O'chirmoqchi bo'lgan kinoning KODINI yozing:</b>\n\n"
        "❌ Bekor qilish: /cancel"
    )
    await state.set_state(AdminStates.waiting_for_delete_code)

@admin_router.message(AdminStates.waiting_for_delete_code, IsAdminFilter())
async def admin_process_delete(message: types.Message, state: FSMContext):
    """Kinoni o'chirish jarayoni"""
    code = message.text.strip().upper()
    movie = await db.get_movie(code)
    
    if movie:        await db.delete_movie(code)
        await message.answer(
            f"✅ <b>{code}</b> kodi bilan kino o'chirildi!",
            reply_markup=get_main_keyboard(is_admin=True)
        )
    else:
        await message.answer("❌ Bunday kodli kino topilmadi!")
    
    await state.clear()

@admin_router.message(F.text == "📊 Statistika", IsAdminFilter())
async def admin_statistics(message: types.Message):
    """To'liq statistika"""
    stats = await db.get_full_statistics()
    text = (
        f"📈 <b>Bot Statistikasi</b>\n\n"
        f"👥 <b>Foydalanuvchilar:</b>\n"
        f"• Jami: {stats['users_count']}\n\n"
        f"🎬 <b>Kinolar:</b>\n"
        f"• Jami: {stats['movies_count']}\n\n"
        f"👁 <b>Ko'rishlar:</b>\n"
        f"• Jami: {stats['total_views']}\n"
        f"• Bugun: {stats['today_views']}\n\n"
        f"📅 Sana: {message.date.strftime('%d.%m.%Y %H:%M')}"
    )
    await message.answer(text)

@admin_router.message(F.text == "👥 Foydalanuvchilar", IsAdminFilter())
async def admin_users(message: types.Message):
    """Foydalanuvchilar ro'yxati"""
    users = await db.get_all_users()
    text = f"👥 <b>Foydalanuvchilar ({len(users)} ta):</b>\n\n"
    
    for user in users[:50]:
        status = "🚫" if user['is_banned'] else "✅"
        username = f"@{user['username']}" if user['username'] else "Yo'q"
        text += f"{status} {user['first_name']} ({username}) - ID: <code>{user['user_id']}</code>\n"
    
    if len(users) > 50:
        text += f"\n... va yana {len(users) - 50} ta"
    
    await message.answer(text)

@admin_router.message(F.text == "📢 Xabar yuborish", IsAdminFilter())
async def admin_broadcast_start(message: types.Message, state: FSMContext):
    """Barcha foydalanuvchilarga xabar yuborish"""
    await message.answer(
        "📢 <b>Barcha foydalanuvchilarga xabar yozing:</b>\n\n"
        "❌ Bekor qilish: /cancel"
    )    await state.set_state(AdminStates.waiting_for_broadcast_message)

@admin_router.message(AdminStates.waiting_for_broadcast_message, IsAdminFilter())
async def admin_process_broadcast(message: types.Message, state: FSMContext):
    """Xabarni yuborish"""
    users = await db.get_all_users()
    success_count = 0
    fail_count = 0
    
    await message.answer(f"📢 Xabar yuborilmoqda... (0/{len(users)})")
    
    for user in users:
        try:
            await bot.send_message(user['user_id'], message.text)
            success_count += 1
        except:
            fail_count += 1
        
        if (success_count + fail_count) % 10 == 0:
            await message.edit_text(f"📢 Xabar yuborilmoqda... ({success_count + fail_count}/{len(users)})")
    
    await message.answer(
        f"✅ <b>Xabar yuborish tugallandi!</b>\n\n"
        f"✅ Muvaffaqiyatli: {success_count}\n"
        f"❌ Xatolik: {fail_count}",
        reply_markup=get_main_keyboard(is_admin=True)
    )
    await state.clear()

@admin_router.callback_query(F.data == "check_subscription", IsAdminFilter())
async def admin_check_sub(callback: types.CallbackQuery):
    await callback.answer("✅ Admin uchun obuna shart emas!", show_alert=True)

@admin_router.callback_query(F.data.startswith("admin_movie_"), IsAdminFilter())
async def admin_movie_detail(callback: types.CallbackQuery):
    """Kino tafsilotlari"""
    movie_id = int(callback.data.split("_")[2])
    # Bu yerda kino tafsilotlarini ko'rsatish mumkin
    await callback.answer("Kino tafsilotlari", show_alert=True)

@admin_router.callback_query(F.data == "admin_menu", IsAdminFilter())
async def admin_menu_back(callback: types.CallbackQuery):
    """Admin menyuga qaytish"""
    stats = await db.get_full_statistics()
    text = (
        f"👤 <b>Admin Panel</b>\n\n"
        f"📊 Foydalanuvchilar: {stats['users_count']}\n"
        f"🎬 Kinolar: {stats['movies_count']}"
    )
    await callback.message.edit_text(text, reply_markup=get_main_keyboard(is_admin=True))
