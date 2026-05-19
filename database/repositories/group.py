# database/repositories/group_repository.py

from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from database.session import AsyncSessionLocal

from database.models.group import (
    Group as GroupTable,
    GroupTopic as GroupTopicTable
)


class GroupRepository:

    # =====================================================
    # GROUPS
    # =====================================================

    async def create_group(
        self,
        tg_id: int,
        title: str,
        is_admin: bool = False,
        is_forum: bool = False
    ) -> GroupTable:

        async with AsyncSessionLocal() as session:

            group = GroupTable(
                tg_id=tg_id,
                title=title,
                is_admin=is_admin,
                is_forum=is_forum
            )

            session.add(group)

            await session.commit()

            # ВАЖНО:
            # загружаем topics сразу
            result = await session.execute(
                select(GroupTable)
                .options(selectinload(GroupTable.topics))
                .where(GroupTable.tg_id == tg_id)
            )

            return result.scalar_one()

    # =====================================================

    async def get_all(self) -> list[GroupTable]:

        async with AsyncSessionLocal() as session:

            result = await session.execute(
                select(GroupTable).options(
                    selectinload(GroupTable.topics)
                )
            )

            return list(result.scalars().unique().all())

    # =====================================================

    async def get_by_tg_id(
        self,
        tg_id: int
    ) -> GroupTable or None:

        async with AsyncSessionLocal() as session:

            result = await session.execute(
                select(GroupTable)
                .options(selectinload(GroupTable.topics))
                .where(GroupTable.tg_id == tg_id)
            )

            return result.scalar_one_or_none()

    # =====================================================

    async def delete_group(
        self,
        tg_id: int
    ) -> None:

        async with AsyncSessionLocal() as session:

            # удаляем топики
            await session.execute(
                delete(GroupTopicTable).where(
                    GroupTopicTable.group_id == tg_id
                )
            )

            # удаляем группу
            await session.execute(
                delete(GroupTable).where(
                    GroupTable.tg_id == tg_id
                )
            )

            await session.commit()

    # =====================================================

    async def upsert_group(
        self,
        tg_id: int,
        title: str,
        is_admin: bool,
        is_forum: bool
    ) -> GroupTable:

        async with AsyncSessionLocal() as session:

            result = await session.execute(
                select(GroupTable).where(
                    GroupTable.tg_id == tg_id
                )
            )

            group = result.scalar_one_or_none()

            # UPDATE
            if group:

                group.title = title
                group.is_admin = is_admin
                group.is_forum = is_forum

            # CREATE
            else:

                group = GroupTable(
                    tg_id=tg_id,
                    title=title,
                    is_admin=is_admin,
                    is_forum=is_forum
                )

                session.add(group)

            await session.commit()

            # ВАЖНО:
            # повторно загружаем вместе с topics
            result = await session.execute(
                select(GroupTable)
                .options(selectinload(GroupTable.topics))
                .where(GroupTable.tg_id == tg_id)
            )

            return result.scalar_one()

    # =====================================================
    # TOPICS
    # =====================================================

    async def upsert_topic(
        self,
        group_id: int,
        topic_id: int,
        topic_title: str
    ) -> GroupTopicTable:

        async with AsyncSessionLocal() as session:

            result = await session.execute(
                select(GroupTopicTable).where(
                    GroupTopicTable.group_id == group_id,
                    GroupTopicTable.topic_id == topic_id
                )
            )

            topic = result.scalar_one_or_none()

            # UPDATE
            if topic:

                topic.topic_title = topic_title

            # CREATE
            else:

                topic = GroupTopicTable(
                    group_id=group_id,
                    topic_id=topic_id,
                    topic_title=topic_title
                )

                session.add(topic)

            await session.commit()
            await session.refresh(topic)

            return topic

    # =====================================================

    async def delete_topic(
        self,
        group_id: int,
        topic_id: int
    ) -> None:

        async with AsyncSessionLocal() as session:

            await session.execute(
                delete(GroupTopicTable).where(
                    GroupTopicTable.group_id == group_id,
                    GroupTopicTable.topic_id == topic_id
                )
            )

            await session.commit()

    # =====================================================

    async def get_topics(
        self,
        group_id: int
    ) -> list[GroupTopicTable]:

        async with AsyncSessionLocal() as session:

            result = await session.execute(
                select(GroupTopicTable).where(
                    GroupTopicTable.group_id == group_id
                )
            )

            return list(result.scalars().all())