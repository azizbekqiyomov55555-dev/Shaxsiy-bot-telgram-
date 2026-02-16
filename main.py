import asyncio
import logging
import os
from pathlib import Path
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
ADMIN_ID = os.getenv("ADMIN_ID")
CHANNEL_ID = os.getenv("CHANNEL_ID")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Logs papkasini yaratish (agar yo'q bo'lsa)
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Log sozlamalari
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/bot.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Bot va Dispatcher yaratish
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Routerlarni qo'shish (bot ni routerlarga o'tkazamiz)
dp.include_router(admin_router)
dp.include_router(user_router)
dp.include_router(common_router)

async def on_startup():
    """Ishga tushish"""
    logger.info("🚀 Bot ishga tushmoqda...")
    logger.info(f"📝 Admin ID: {ADMIN_ID}")
    logger.info(f"📢 Channel: {CHANNEL_ID}")
    
    try:
        await db.connect()
        logger.info("✅ Ma'lumotlar bazasiga ulandi")
    except Exception as e:
        logger.error(f"❌ Bazaga ulanishda xatolik: {e}")
        raise
    
    bot_info = await bot.get_me()
    logger.info(f"✅ Bot muvaffaqiyatli ishga tushdi: @{bot_info.username}")

async def on_shutdown():
    """To'xtash"""
    logger.info("🛑 Bot to'xtatilmoqda...")
    try:
        await db.close()
        logger.info("✅ Baza yopildi")
    except Exception as e:
        logger.error(f"❌ Bazani yopishda xatolik: {e}")
    
    try:
        await bot.session.close()
        logger.info("✅ Bot session yopildi")
    except Exception as e:
        logger.error(f"❌ Session yopishda xatolik: {e}")

async def main():
    """Asosiy funksiya"""
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    try:
        logger.info("📡 Polling boshlandi...")
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("⌨️ Keyboard interrupt")
    except Exception as e:
        logger.error(f"❌ Critical error: {e}")
        raise
    finally:
        await on_shutdown()

if __name__ == "__main__":
    asyncio.run(main())
