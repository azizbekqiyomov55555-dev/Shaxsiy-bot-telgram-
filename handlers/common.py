from aiogram import Router, F, types
from aiogram.filters import Command
from database import db
import logging

logger = logging.getLogger(__name__)
common_router = Router()

@common_router.message(Command("cancel"))
async def cmd_cancel(message: types.Message, state):
    """Holatni bekor qilish"""
    await state.clear()
    await message.answer("❌ Amal bekor qilindi.", reply_markup=get_main_keyboard(is_admin=False))

@common_router.message(Command("help"))
async def cmd_help(message: types.Message):
    """Yordam"""
    text = (
        "❓ <b>Yordam</b>\n\n"
        "📚 <b>Buyruqlar:</b>\n"
        "/start - Botni boshlash\n"
        "/help - Yordam\n"
        "/cancel - Amalni bekor qilish\n\n"
        "🎬 <b>Kino ko'rish:</b>\n"
        "1. Kanalga obuna bo'ling\n"
        "2. 'Kino izlash' tugmasini bosing\n"
        "3. Kodni kiriting\n\n"
        "📞 Savollar: @admin_username"
    )
    await message.answer(text)

@common_router.message(Command("stats"))
async def cmd_stats(message: types.Message):
    """Statistika (hamma uchun)"""
    stats = await db.get_full_statistics()
    text = (
        f"📊 <b>Bot Statistikasi</b>\n\n"
        f"👥 Foydalanuvchilar: {stats['users_count']}\n"
        f"🎬 Kinolar: {stats['movies_count']}\n"
        f"👁 Jami ko'rishlar: {stats['total_views']}"
    )
    await message.answer(text)

@common_router.errors()
async def error_handler(event, error):
    """Xatoliklarni qayta ishlash"""
    logger.error(f"Xatolik: {error}")
