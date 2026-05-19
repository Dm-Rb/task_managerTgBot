from telegram_bot.models.group import Group


class GroupCache:

    def __init__(self):
        self._groups: dict[int, Group] = {}

    def get(self, tg_id: int) -> Group or None:
        """
        Получить группу по telegram id
        """
        return self._groups.get(tg_id)

    def delete(self, tg_id: int) -> None:
        """
        Удалить группу из кеша
        """
        self._groups.pop(tg_id, None)

    def exists(self, tg_id: int) -> bool:
        """
        Проверка существования группы
        """
        return tg_id in self._groups

    def all(self) -> list[Group]:
        """
        Получить список всех групп
        """
        return list(self._groups.values())

    # =====================================================
    # CRUD
    # =====================================================

    def add(self, group: Group) -> Group:
        """
        Добавить новую группу
        """
        self._groups[group.tg_id] = group

        return group

    def update(self, group: Group) -> Group:
        """
        Обновить существующую группу
        """

        existing = self._groups.get(group.tg_id)

        # если группы нет — создаём
        if not existing:
            self._groups[group.tg_id] = group
            return group

        existing.title = group.title
        existing.is_admin = group.is_admin
        existing.is_forum = group.is_forum
        existing.topics = group.topics

        return existing

    def upsert(self, group: Group) -> Group:
        """
        Добавить или обновить группу
        """

        if self.exists(group.tg_id):
            return self.update(group)

        return self.add(group)