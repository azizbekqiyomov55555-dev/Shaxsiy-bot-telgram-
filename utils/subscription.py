from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
import logging
import os

logger = logging.getLogger(__name__)

async def check_subscription(user_id: int, channel_id: str) -> bool:
    """Foydalanuvchi kanalga obuna bo'lganligini tekshirish"""
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    try:
        member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
        is_subscribed = member.status in ["member", "administrator", "creator"]
        await bot.session.close()
        return is_subscribed
    except TelegramBadRequest as e:
        logger.error(f"Obunani tekshirishda xatolik: {e}")
        await bot.session.close()
        return False
    except Exception as e:
        logger.error(f"Obunani tekshirishda kutilmagan xatolik: {e}")
        await bot.session.close()
        return False
