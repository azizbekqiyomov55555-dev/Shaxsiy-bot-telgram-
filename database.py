import aiosqlite
import asyncio
from datetime import datetime
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path: str = "kino_bot.db"):
        self.db_path = db_path
        self.connection: Optional[aiosqlite.Connection] = None
    
    async def connect(self):
        """Bazaga ulanish"""
        self.connection = await aiosqlite.connect(self.db_path)
        self.connection.row_factory = aiosqlite.Row
        await self.create_tables()
        logger.info("✅ Ma'lumotlar bazasiga ulanish muvaffaqiyatli amalga oshirildi")
    
    async def close(self):
        """Bazadan uzilish"""
        if self.connection:
            await self.connection.close()
            logger.info("🔌 Ma'lumotlar bazasidan uzilish amalga oshirildi")
    
    async def create_tables(self):
        """Jadvallarni yaratish"""
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                is_banned INTEGER DEFAULT 0,
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                file_id TEXT NOT NULL,
                file_type TEXT DEFAULT 'video',
                caption TEXT,
                views INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS movie_views (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                movie_id INTEGER NOT NULL,
                viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (movie_id) REFERENCES movies(id)
            )
        """)
        
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS bot_settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await self.connection.commit()
        logger.info("📊 Barcha jadvallar yaratildi")
    
    # ================= USER OPERATSIYALARI =================
    
    async def add_user(self, user_id: int, username: str, first_name: str, last_name: str = None):
        """Yangi foydalanuvchini qo'shish"""
        try:
            await self.connection.execute("""
                INSERT OR IGNORE INTO users (user_id, username, first_name, last_name)
                VALUES (?, ?, ?, ?)
            """, (user_id, username, first_name, last_name))
            await self.connection.execute("""
                UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE user_id = ?
            """, (user_id,))
            await self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"Foydalanuvchini qo'shishda xatolik: {e}")
            return False
    
    async def get_user(self, user_id: int) -> Optional[Dict]:
        """Foydalanuvchini olish"""
        cursor = await self.connection.execute(
            "SELECT * FROM users WHERE user_id = ?", (user_id,)
        )
        row = await cursor.fetchone()        return dict(row) if row else None
    
    async def ban_user(self, user_id: int):
        """Foydalanuvchini ban qilish"""
        await self.connection.execute(
            "UPDATE users SET is_banned = 1 WHERE user_id = ?", (user_id,)
        )
        await self.connection.commit()
    
    async def unban_user(self, user_id: int):
        """Foydalanuvchini ban dan chiqarish"""
        await self.connection.execute(
            "UPDATE users SET is_banned = 0 WHERE user_id = ?", (user_id,)
        )
        await self.connection.commit()
    
    async def get_all_users(self) -> List[Dict]:
        """Barcha foydalanuvchilarni olish"""
        cursor = await self.connection.execute("SELECT * FROM users")
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    
    async def get_users_count(self) -> int:
        """Foydalanuvchilar sonini olish"""
        cursor = await self.connection.execute("SELECT COUNT(*) FROM users")
        result = await cursor.fetchone()
        return result[0] if result else 0
    
    # ================= MOVIE OPERATSIYALARI =================
    
    async def add_movie(self, code: str, file_id: str, file_type: str, caption: str) -> bool:
        """Kino qo'shish"""
        try:
            await self.connection.execute("""
                INSERT INTO movies (code, file_id, file_type, caption)
                VALUES (?, ?, ?, ?)
            """, (code.upper(), file_id, file_type, caption))
            await self.connection.commit()
            return True
        except aiosqlite.IntegrityError:
            return False
        except Exception as e:
            logger.error(f"Kino qo'shishda xatolik: {e}")
            return False
    
    async def get_movie(self, code: str) -> Optional[Dict]:
        """Kod bo'yicha kinoni olish"""
        cursor = await self.connection.execute(
            "SELECT * FROM movies WHERE code = ? AND is_active = 1", (code.upper(),)
        )        row = await cursor.fetchone()
        return dict(row) if row else None
    
    async def get_all_movies(self) -> List[Dict]:
        """Barcha kinolarni olish"""
        cursor = await self.connection.execute("SELECT * FROM movies ORDER BY created_at DESC")
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    
    async def delete_movie(self, code: str) -> bool:
        """Kinoni o'chirish"""
        cursor = await self.connection.execute(
            "DELETE FROM movies WHERE code = ?", (code.upper(),)
        )
        await self.connection.commit()
        return cursor.rowcount > 0
    
    async def update_movie_views(self, movie_id: int):
        """Ko'rishlar sonini yangilash"""
        await self.connection.execute("""
            UPDATE movies SET views = views + 1 WHERE id = ?
        """, (movie_id,))
        await self.connection.commit()
    
    async def add_movie_view(self, user_id: int, movie_id: int):
        """Ko'rish tarixini qo'shish"""
        await self.connection.execute("""
            INSERT INTO movie_views (user_id, movie_id)
            VALUES (?, ?)
        """, (user_id, movie_id))
        await self.connection.commit()
    
    async def get_movie_stats(self, movie_id: int) -> int:
        """Kino ko'rishlar sonini olish"""
        cursor = await self.connection.execute(
            "SELECT COUNT(*) FROM movie_views WHERE movie_id = ?", (movie_id,)
        )
        result = await cursor.fetchone()
        return result[0] if result else 0
    
    async def get_movies_count(self) -> int:
        """Kinolar sonini olish"""
        cursor = await self.connection.execute("SELECT COUNT(*) FROM movies WHERE is_active = 1")
        result = await cursor.fetchone()
        return result[0] if result else 0
    
    async def search_movies(self, query: str) -> List[Dict]:
        """Kinolarni qidirish"""
        cursor = await self.connection.execute("""
            SELECT * FROM movies             WHERE (caption LIKE ? OR code LIKE ?) AND is_active = 1
            ORDER BY created_at DESC
        """, (f'%{query}%', f'%{query}%'))
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    
    # ================= SETTINGS OPERATSIYALARI =================
    
    async def get_setting(self, key: str) -> Optional[str]:
        """Sozlamani olish"""
        cursor = await self.connection.execute(
            "SELECT value FROM bot_settings WHERE key = ?", (key,)
        )
        row = await cursor.fetchone()
        return row[0] if row else None
    
    async def set_setting(self, key: str, value: str):
        """Sozlamani o'rnatish"""
        await self.connection.execute("""
            INSERT OR REPLACE INTO bot_settings (key, value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, (key, value))
        await self.connection.commit()
    
    # ================= STATISTIKA =================
    
    async def get_full_statistics(self) -> Dict[str, Any]:
        """To'liq statistikani olish"""
        users_count = await self.get_users_count()
        movies_count = await self.get_movies_count()
        
        cursor = await self.connection.execute("""
            SELECT SUM(views) FROM movies
        """)
        total_views = await cursor.fetchone()
        
        cursor = await self.connection.execute("""
            SELECT COUNT(*) FROM movie_views WHERE date(viewed_at) = date('now')
        """)
        today_views = await cursor.fetchone()
        
        return {
            'users_count': users_count,
            'movies_count': movies_count,
            'total_views': total_views[0] if total_views else 0,
            'today_views': today_views[0] if today_views else 0
        }

# Global DB instance
db = Database()
