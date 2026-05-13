from sqlalchemy import select, delete
from database.session import AsyncSessionLocal
from database.models.group import Group as GroupTable
from telegram_bot.models.group import Group as GroupDTO


class GroupRepository:

    # -------------------------
    # CREATE GROUP
    # -------------------------
    async def create(
        self,
        tg_id: int,
        title: str,
        is_admin: bool = False,
    ) -> GroupTable:

        async with AsyncSessionLocal() as session:

            group = GroupTable(
                tg_id=tg_id,
                title=title,
                is_admin=is_admin,
            )

            session.add(group)
            await session.commit()
            await session.refresh(group)

            return group

    async def get_all(self) -> list[GroupTable]:

        async with AsyncSessionLocal() as session:

            result = await session.execute(
                select(GroupTable)
            )

            return list(result.scalars().all())

    # -------------------------
    # GET BY TG_ID
    # -------------------------
    async def get_by_tg_id(self, tg_id: int) -> GroupTable or None:

        async with AsyncSessionLocal() as session:

            result = await session.execute(
                select(GroupTable).where(GroupTable.tg_id == tg_id)
            )

            return result.scalar_one_or_none()

    # -------------------------
    # DELETE
    # -------------------------
    async def delete(self, tg_id: int) -> None:

        async with AsyncSessionLocal() as session:

            await session.execute(
                delete(GroupTable).where(GroupTable.tg_id == tg_id)
            )

            await session.commit()

    # -------------------------
    # UPSERT
    # -------------------------
    async def upsert(
        self,
        tg_id: int,
        title: str,
        is_admin: bool,
    ) -> GroupTable:

        async with AsyncSessionLocal() as session:

            result = await session.execute(
                select(GroupTable).where(GroupTable.tg_id == tg_id)
            )

            group = result.scalar_one_or_none()

            if group:
                group.title = title
                group.is_admin = is_admin
            else:
                group = GroupTable(
                    tg_id=tg_id,
                    title=title,
                    is_admin=is_admin,
                )
                session.add(group)

            await session.commit()
            await session.refresh(group)

            return group
