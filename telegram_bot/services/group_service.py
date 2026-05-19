from telegram_bot.models.group import Group, GroupTopic


class GroupService:

    def __init__(self, cache, database):
        self.cache = cache
        self.database = database

    # =====================================================
    # WARM UP
    # =====================================================

    async def warm_up(self):

        groups = await self.database.get_all()

        if not groups:
            return

        for row in groups:

            group = Group(
                tg_id=row.tg_id,
                title=row.title,
                is_admin=row.is_admin,
                is_forum=row.is_forum,
                topics=[]
            )

            # topics relationship
            for topic in row.topics:
                group.topics.append(
                    GroupTopic(
                        topic_id=topic.topic_id,
                        title=topic.topic_title
                    )
                )

            self.cache.upsert(group)

    # =====================================================
    # GROUPS
    # =====================================================

    async def add_group(self, group: Group):

        self.cache.upsert(group)

        # сохраняем группу
        await self.database.upsert_group(
            tg_id=group.tg_id,
            title=group.title,
            is_admin=group.is_admin,
            is_forum=group.is_forum
        )

        # сохраняем топики
        for topic in group.topics:

            await self.database.upsert_topic(
                group_id=group.tg_id,
                topic_id=topic.topic_id,
                topic_title=topic.title
            )

    async def remove_group(self, tg_id: int):

        self.cache.delete(tg_id)

        await self.database.delete_group(tg_id)

    def get_all_groups(self) -> list[Group]:
        return self.cache.all()

    def get_group_by_id(self, group_id) -> Group or None:
        return self.cache.get(group_id)

    # =====================================================
    # TOPICS
    # =====================================================

    async def add_topic(
        self,
        group_id: int,
        topic: GroupTopic
    ) -> bool:

        group = self.cache.get(group_id)

        if not group:
            return False

        exists = any(
            t.topic_id == topic.topic_id
            for t in group.topics
        )

        if exists:
            return False

        group.topics.append(topic)

        await self.database.upsert_topic(
            group_id=group_id,
            topic_id=topic.topic_id,
            topic_title=topic.title
        )

        return True

    async def remove_topic(
            self,
            group_id: int,
            topic_id: int
    ):

        group = self.cache.get(group_id)

        if group:
            group.topics = [
                t for t in group.topics
                if t.topic_id != topic_id
            ]

        await self.database.delete_topic(
            group_id=group_id,
            topic_id=topic_id
        )

    def get_topics(
        self,
        group_id: int
    ) -> list[GroupTopic]:

        group = self.cache.get(group_id)

        if not group:
            return []

        return group.topics

    def get_topic(
        self,
        group_id: int,
        topic_id: int
    ) -> GroupTopic or None:

        group = self.cache.get(group_id)

        if not group:
            return None

        for topic in group.topics:

            if topic.topic_id == topic_id:
                return topic

        return None