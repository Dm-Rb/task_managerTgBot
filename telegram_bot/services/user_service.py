from telegram_bot.models.user import User
from core.config import settings
from telegram_bot.storage.user_cache import UserCache


class UserService:
    def __init__(self, cache: UserCache, database):
        self.cache: UserCache = cache
        self.database = database

    async def warm_up(self):
        """ прогрев кеша и гоев из базы данных """
        users = await self.database.get_all()

        for db_user in users:
            user_ = User(
                    tg_id=db_user.tg_id,
                    first_name=db_user.first_name,
                    last_name=db_user.last_name,
                    role=db_user.role,
                    is_banned=db_user.is_banned,
                    failed_attempts=0
                )
            self.cache.set(user_)

    def get_employee_users(self) -> list[User] or list:

        result = []

        users = self.cache.all()
        for user in users.values():
            # только сотрудники
            if user.role != 1:
                continue
            result.append(user)
        #
        return result

    async def register_in_cache(self, tg_user) -> User:
        user = self.cache.get(tg_user.id)

        if not user:
            user = User(
                tg_id=tg_user.id,
                first_name=tg_user.first_name,
                last_name=tg_user.last_name or "",
            )
            await self.cache.upsert(user)

        return user

    async def password(self, user, password: str) -> bool or None:
        """Проверяет пароль, задаёт роль на основании пароля и записывает в БД"""

        if user.is_banned:
            return

        password = password.strip().lower()

        # admin
        if password == settings.ADMIN_PSW.strip().lower():
            user.role = 2
            user.failed_attempts = 0
            await self.database.create(user.tg_id, user.first_name, user.last_name, user.role, 0)
            return True

        # user
        if password == settings.USER_PSW.strip().lower():
            user.role = 1
            user.failed_attempts = 0
            await self.database.create(user.tg_id, user.first_name, user.last_name, user.role, 0)
            return True

        # invalid
        user.failed_attempts += 1

        if int(user.failed_attempts) >= int(settings.MAX_ATTS_PSW):
            await self.database.create(user.tg_id, user.first_name, user.last_name, user.role, 1)
            user.is_banned = True
            return None

        return

    async def logout(self, tg_id: int) -> bool:

        # получаем пользователя из кеша
        user = self.cache.get(tg_id)
        if not user:
            return False

        # сбрасываем роль в кеше
        user.role = 0
        # удаляем из БД
        await self.database.delete(tg_id)

        return True

    async def is_user_admin(self, tg_id: int) -> bool:
        user = self.cache.get(tg_id)
        if not user:
            return False
        if user.role == 2:
            return True
        return False

    async def get_performers_in_group(self, bot, group_id: int) -> list:
        """Возвращает список сотрудников, которые состоят в указсанной группе"""
        employee_users = self.get_employee_users()  # получаем user.role == 2
        performers = []

        for employee in employee_users:
            try:
                member = await bot.get_chat_member(
                    chat_id=group_id,
                    user_id=employee.tg_id
                )
                if member.status in ("member", "administrator", "creator"):
                    performers.append(employee)
            except Exception:
                continue

        return performers
