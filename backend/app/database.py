import asyncpg
from config import DB_DSN

class Database:
    def __init__(self, dsn):
        self.dsn = dsn
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(self.dsn)

    # ============================
    # Пользователи
    # ============================

    async def create_user(self, vk_id: int, name: str):
        query = """
        INSERT INTO users (vk_id, name)
        VALUES ($1, $2)
        RETURNING id;
        """
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, vk_id, name)

    async def get_user_by_vk_id(self, vk_id: int):
        query = "SELECT * FROM users WHERE vk_id = $1;"
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, vk_id)

    async def ensure_user_exists(self, user_id: int):
        """
        Автоматически создает запись пользователя, если её еще нет в таблице users.
        Если пользователь уже существует, благодаря ON CONFLICT запрос ничего не ломает.
        """
        query = """
        INSERT INTO users (id, vk_id, name)
        VALUES ($1, $2, $3)
        ON CONFLICT (id) DO NOTHING;
        """
        async with self.pool.acquire() as conn:
            await conn.execute(query, user_id, user_id, f"Пользователь {user_id}")

    # 🔥 ДОБАВЛЕНО: Обновление имени пользователя (избавляемся от "Пользователь XX")
    async def update_user_name(self, vk_id: int, new_name: str):
        query = "UPDATE users SET name = $1 WHERE vk_id = $2;"
        async with self.pool.acquire() as conn:
            await conn.execute(query, new_name, vk_id)

    # ============================
    # Семьи
    # ============================

    async def create_family(self, name: str, invite_code: str):
        query = """
        INSERT INTO families (name, invite_code)
        VALUES ($1, $2)
        RETURNING id;
        """
        async with self.pool.acquire() as conn:
            return await conn.fetch
