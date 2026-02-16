from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from database import db
import os

class IsAdminFilter(BaseFilter):
    """Admin tekshiruvi"""
    async def __call__(self, obj: Message | CallbackQuery) -> bool:
        admin_id = int(os.getenv("ADMIN_ID"))
        user_id = obj.from_user.id
        return user_id == admin_id

class IsSubscribedFilter(BaseFilter):
    """Obuna tekshiruvi"""
    def __init__(self, channel_id: str):
        self.channel_id = channel_id
    
    async def __call__(self, obj: Message | CallbackQuery) -> bool:
        from utils.subscription import check_subscription
        return await check_subscription(obj.from_user.id, self.channel_id)

class IsNotBannedFilter(BaseFilter):
    """Ban tekshiruvi"""
    async def __call__(self, obj: Message | CallbackQuery) -> bool:
        user = await db.get_user(obj.from_user.id)
        if user is None:
            return True
        return user.get('is_banned', 0) == 0
