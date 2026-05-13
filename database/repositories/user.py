from sqlalchemy import select, update, delete
from database.session import AsyncSessionLocal
from database.models.user import UserTable


class UserRepository:

    # -------------------------
    # CREATE USER
    # -------------------------
    async def create(
        self,
        tg_id: int,
        first_name: str,
        last_name: str = "",
        role: int = 0,
        is_banned: bool = False,
    ) -> UserTable:

        async with AsyncSessionLocal() as session:
            user = UserTable(
                tg_id=tg_id,
                first_name=first_name,
                last_name=last_name,
                role=role,
                is_banned=is_banned,
            )

            session.add(user)
            await session.commit()
            await session.refresh(user)

            return user

    async def get_all(self) -> list[UserTable]:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(UserTable)
            )
            return list(result.scalars().all())

    async def delete(self, tg_id: int):

        async with AsyncSessionLocal() as session:
            await session.execute(
                delete(UserTable).where(UserTable.tg_id == tg_id)
            )

            await session.commit()

    # -------------------------
    # GET BY TG_ID
    # -------------------------
    async def get_by_tg_id(self, tg_id: int) -> UserTable or None:

        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(UserTable).where(UserTable.tg_id == tg_id)
            )
            return result.scalar_one_or_none()

    # -------------------------
    # UPSERT (create or update basic fields)
    # -------------------------
    async def upsert(
        self,
        tg_id: int,
        first_name: str,
        last_name: str = "",
    ) -> UserTable:

        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(UserTable).where(UserTable.tg_id == tg_id)
            )
            user = result.scalar_one_or_none()

            if user:
                user.first_name = first_name
                user.last_name = last_name
            else:
                user = UserTable(
                    tg_id=tg_id,
                    first_name=first_name,
                    last_name=last_name,
                )
                session.add(user)

            await session.commit()
            await session.refresh(user)

            return user

    # -------------------------
    # SET ROLE
    # -------------------------
    async def set_role(self, tg_id: int, role: int) -> UserTable or None:

        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(UserTable).where(UserTable.tg_id == tg_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                return None

            user.role = role
            await session.commit()
            await session.refresh(user)

            return user

    # -------------------------
    # BAN USER
    # -------------------------
    async def ban_user(self, tg_id: int) -> UserTable or None:

        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(UserTable).where(UserTable.tg_id == tg_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                return None

            user.is_banned = True
            await session.commit()
            await session.refresh(user)

            return user

    # -------------------------
    # UNBAN USER (optional)
    # -------------------------
    async def unban_user(self, tg_id: int) -> UserTable or None:

        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(UserTable).where(UserTable.tg_id == tg_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                return None

            user.is_banned = False
            await session.commit()
            await session.refresh(user)

            return user