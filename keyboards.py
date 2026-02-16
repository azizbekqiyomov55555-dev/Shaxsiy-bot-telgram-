from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from typing import Optional

def get_main_keyboard(is_admin: bool = False) -> ReplyKeyboardMarkup:
    """Asosiy menyu"""
    if is_admin:
        keyboard = [
            [
                KeyboardButton(text="🎬 Yangi kino qo'shish"),
                KeyboardButton(text="📋 Kinolar ro'yxati")
            ],
            [
                KeyboardButton(text="🗑 Kinoni o'chirish"),
                KeyboardButton(text="📊 Statistika")
            ],
            [
                KeyboardButton(text="👥 Foydalanuvchilar"),
                KeyboardButton(text="⚙️ Sozlamalar")
            ],
            [
                KeyboardButton(text="📢 Xabar yuborish")
            ]
        ]
    else:
        keyboard = [
            [
                KeyboardButton(text="🎥 Kino izlash")
            ],
            [
                KeyboardButton(text="📢 Kanalimiz"),
                KeyboardButton(text="📞 Aloqa")
            ],
            [
                KeyboardButton(text="🔍 Qidiruv")
            ]
        ]
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Menyuni tanlang..."
    )

def get_channel_keyboard(channel_id: str) -> InlineKeyboardMarkup:
    """Kanalga obuna bo'lish tugmasi"""
    channel_username = channel_id.replace('@', '') if channel_id.startswith('@') else channel_id
    keyboard = [
        [
            InlineKeyboardButton(
                text="📢 Kanalga obuna bo'lish",                url=f"https://t.me/{channel_username}"
            )
        ],
        [
            InlineKeyboardButton(
                text="✅ Obunani tekshirish",
                callback_data="check_subscription"
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_movie_keyboard(movie_code: str) -> InlineKeyboardMarkup:
    """Kino uchun tugmalar"""
    keyboard = [
        [
            InlineKeyboardButton(
                text="📥 Yuklab olish",
                callback_data=f"download_{movie_code}"
            ),
            InlineKeyboardButton(
                text="🔗 Ulashish",
                callback_data=f"share_{movie_code}"
            )
        ],
        [
            InlineKeyboardButton(
                text="🔙 Orqaga",
                callback_data="back_to_menu"
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_admin_movie_list_keyboard(movies: list) -> InlineKeyboardMarkup:
    """Admin uchun kinolar ro'yxati"""
    keyboard = []
    for movie in movies[:10]:  # Birinchi 10 ta
        keyboard.append([
            InlineKeyboardButton(
                text=f"🎬 {movie['code']} ({movie['views']}👁)",
                callback_data=f"admin_movie_{movie['id']}"
            )
        ])
    
    if len(movies) > 10:
        keyboard.append([
            InlineKeyboardButton(text="➡️ Keyingi", callback_data="movies_page_2")
        ])
        keyboard.append([
        InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_menu")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_confirmation_keyboard(confirm_data: str, cancel_data: str) -> InlineKeyboardMarkup:
    """Tasdiqlash tugmalari"""
    keyboard = [
        [
            InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=confirm_data),
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data=cancel_data)
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_users_keyboard() -> InlineKeyboardMarkup:
    """Foydalanuvchilar boshqaruvi"""
    keyboard = [
        [
            InlineKeyboardButton(text="📊 Barcha foydalanuvchilar", callback_data="all_users"),
            InlineKeyboardButton(text="🚫 Ban qilinganlar", callback_data="banned_users")
        ],
        [
            InlineKeyboardButton(text="🔙 Admin panel", callback_data="admin_menu")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_settings_keyboard() -> InlineKeyboardMarkup:
    """Sozlamalar tugmalari"""
    keyboard = [
        [
            InlineKeyboardButton(text="📝 Xabar matnini o'zgartirish", callback_data="edit_welcome"),
            InlineKeyboardButton(text="🔔 Obuna sozlamalari", callback_data="sub_settings")
        ],
        [
            InlineKeyboardButton(text="🔙 Admin panel", callback_data="admin_menu")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
