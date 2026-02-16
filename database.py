import sqlite3
import aiosqlite
from typing import Optional, Dict, List, Any
import logging

# Logger sozlash
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_file: str = "bot_database.db"):
        self.db_file = db_file
        self.connection: Optional[aiosqlite.Connection] = None

    async def connect(self):
        """Ma'lumotlar bazasiga ulanish"""
        self.connection = await aiosqlite.connect(self.db_file)
        self.connection.row_factory = aiosqlite.Row  # Natijani dict ko'rinishida olish uchun
        await self.create_tables()

    async def create_tables(self):
        """Jadvallarni yaratish (agar yo'q bo'lsa)"""
        async with self.connection.cursor() as cursor:
            # Foydalanuvchilar jadvali
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Kinolar jadvali
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS movies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT UNIQUE NOT NULL,
                    caption TEXT,
                    file_id TEXT,
                    file_type TEXT,
                    views INTEGER DEFAULT 0,
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Ko'rishlar tarixi
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS movie_views (                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    movie_id INTEGER,
                    viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(user_id),
                    FOREIGN KEY(movie_id) REFERENCES movies(id)
                )
            """)
            
            # Sozlamalar
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS bot_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            await self.connection.commit()

    async def close(self):
        """Ulanishni yopish"""
        if self.connection:
            await self.connection.close()

    # ================= FOYDALANUVCHI OPERATSIYALARI =================
    
    async def add_user(self, user_id: int, username: str, first_name: str) -> bool:
        """Yangi foydalanuvchini qo'shish"""
        try:
            await self.connection.execute(
                "INSERT OR IGNORE INTO users (user_id, username, first_name) VALUES (?, ?, ?)",
                (user_id, username, first_name)
            )
            await self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"Foydalanuvchi qo'shishda xatolik: {e}")
            return False
    
    async def get_user(self, user_id: int) -> Optional[Dict]:
        """Foydalanuvchini olish"""
        cursor = await self.connection.execute(
            "SELECT * FROM users WHERE user_id = ?", (user_id,)
        )
        row = await cursor.fetchone()
        return dict(row) if row else None

    async def get_users_count(self) -> int:
        """Foydalanuvchilar sonini olish"""        cursor = await self.connection.execute("SELECT COUNT(*) FROM users")
        result = await cursor.fetchone()
        return result[0] if result else 0

    # ================= KINO OPERATSIYALARI =================
    
    async def add_movie(self, code: str, caption: str, file_id: str, file_type: str) -> bool:
        """Kinoni bazaga qo'shish"""
        try:
            await self.connection.execute(
                """INSERT INTO movies (code, caption, file_id, file_type) 
                   VALUES (?, ?, ?, ?)""",
                (code.upper(), caption, file_id, file_type)
            )
            await self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"Kino qo'shishda xatolik: {e}")
            return False
    
    async def get_movie(self, code: str) -> Optional[Dict]:
        """Kod bo'yicha kinoni olish"""
        # BU YERDA XATO BOR EDI, TO'G'RILANDI:
        cursor = await self.connection.execute(
            "SELECT * FROM movies WHERE code = ? AND is_active = 1", 
            (code.upper(),)
        )
        row = await cursor.fetchone()
        return dict(row) if row else None
    
    async def get_all_movies(self) -> List[Dict]:
        """Barcha kinolarni olish"""
        cursor = await self.connection.execute("SELECT * FROM movies ORDER BY created_at DESC")
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    
    async def delete_movie(self, code: str) -> bool:
        """Kinoni o'chirish (faqat is_active ni 0 qilamiz)"""
        cursor = await self.connection.execute(
            "UPDATE movies SET is_active = 0 WHERE code = ?", 
            (code.upper(),)
        )
        await self.connection.commit()
        return cursor.rowcount > 0
    
    async def update_movie_views(self, movie_id: int):
        """Ko'rishlar sonini yangilash"""
        await self.connection.execute("""
            UPDATE movies SET views = views + 1 WHERE id = ?
        """, (movie_id,))        await self.connection.commit()
    
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
        # SQL so'rovi to'g'rilandi
        cursor = await self.connection.execute("""
            SELECT * FROM movies 
            WHERE (caption LIKE ? OR code LIKE ?) AND is_active = 1
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
            VALUES (?, ?, CURRENT_TIMESTAMP)        """, (key, value))
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
