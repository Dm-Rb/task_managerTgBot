from telegram_bot.models.user import User
from .base import BaseCache


class UserCache(BaseCache):
    def __init__(self):
        super().__init__()
        self.users: dict[int, User] = {}

    async def upsert(self, user: User) -> User:
        async with self._lock:
            existing = self.users.get(user.tg_id)

            if existing:
                existing.first_name = user.first_name
                existing.last_name = user.last_name
                existing.role = user.role
                return existing

            self.users[user.tg_id] = user
            return user

    def get(self, tg_id: int) -> User or None:
        return self.users.get(tg_id)

    def all(self):
        return self.users

    def set(self, user: User) -> None:
        """
        Добавить или обновить пользователя в кеше
        """
        self.users[user.tg_id] = user
