import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv

from database import db
from handlers.admin import admin_router
from handlers.user import user_router
from handlers.common import common_router

# Sozlamalarni yuklash
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Log sozlamalari
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Bot va Dispatcher yaratish
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Routerlarni qo'shish
dp.include_router(admin_router)
dp.include_router(user_router)
dp.include_router(common_router)

# Global bot referensini qo'shish
import handlers.admin
import handlers.user
handlers.admin.bot = bot
handlers.user.bot = bot

async def on_startup():
    """Ishga tushish"""
    logger.info("🚀 Bot ishga tushmoqda...")
    await db.connect()
    logger.info("✅ Bot muvaffaqiyatli ishga tushdi!")

async def on_shutdown():
    """To'xtash"""
    logger.info("🛑 Bot to'xtatilmoqda...")
    await db.close()
    await bot.session.close()
    logger.info("✅ Bot to'xtatildi!")

async def main():
    """Asosiy funksiya"""
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("⌨️ Keyboard interrupt")
    except Exception as e:
        logger.error(f"❌ Xatolik: {e}")
    finally:
        await on_shutdown()

if __name__ == "__main__":
    asyncio.run(main())
