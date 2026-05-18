from telegram_bot.models.group import Group
from telegram_bot.storage.group_cache import GroupCache



class GroupService:

    def __init__(self, cache: GroupCache, database):
        self.cache = cache
        self.database = database

    async def warm_up(self):
        """
        Загружает все группы из базы данных в кеш при старте бота
        """
        groups = await self.database.get_all()

        if not groups:
            return

        for g in groups:
            self.cache.upsert(
                Group(
                    tg_id=g.tg_id,
                    title=g.title,
                    is_admin=g.is_admin
                )
            )

        return

    async def add_group(self, group):

        self.cache.upsert(group)

        await self.database.upsert(
            tg_id=group.tg_id,
            title=group.title,
            is_admin=group.is_admin
        )

    async def remove_group(self, tg_id: int):

        self.cache.delete(tg_id)
        await self.database.delete(tg_id)

    def get_all_groups(self) -> list[Group]:
        """
        Получить все группы из кеша
        """
        return self.cache.all()

    def get_group_by_id(self, group_id) -> Group:
        """
        Получить все группы из кеша
        """
        return self.cache.get(group_id)


