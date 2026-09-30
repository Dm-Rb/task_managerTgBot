from datetime import datetime
from typing import Any
from sqlalchemy import delete, select, update
from database.models.cash_colletrion_task import CashCollectionTaskTable
from database.session import AsyncSessionLocal


class CashCollectionTaskRepository:

    @staticmethod
    def _validate_rows(rows: list[dict[str, Any]]) -> None:
        for row in rows:
            if "id" not in row:
                raise ValueError(f"В словаре нет ключа 'id': {row}")


    async def upsert_many(self, rows: list[dict[str, Any]]) -> list[CashCollectionTaskTable]:
        """
        Создаёт или обновляет несколько строк в одной транзакции.
        Каждый словарь: ключи = имена атрибутов CashCollectionTaskTable,
        обязателен ключ "id". Поиск существующей строки идёт по id.
        """

        if not rows:
            return []

        self._validate_rows(rows)

        valid_columns = {c.name for c in CashCollectionTaskTable.__table__.columns}

        async with AsyncSessionLocal() as session:

            merged = []
            for row in rows:
                filtered = {k: v for k, v in row.items() if k in valid_columns}
                merged.append(await session.merge(CashCollectionTaskTable(**filtered)))

            await session.commit()

            return merged

    async def upsert(self, row: dict[str, Any]) -> CashCollectionTaskTable:
        """Создаёт строку или обновляет существующую (поиск по id)."""

        result = await self.upsert_many([row])
        return result[0]

    async def update_status(
        self,
        task_id: str,
        status: str,
        completed_at: datetime | None = None,
        comment: str | None = None
    ) -> bool:
        """
        Точечное обновление статуса существующей строки.
        Возвращает True, если строка найдена и обновлена.
        В отличие от upsert, не пытается создать новую строку.
        """

        async with AsyncSessionLocal() as session:

            result = await session.execute(
                update(CashCollectionTaskTable)
                .where(CashCollectionTaskTable.id == task_id)
                .values(status=status, completed_at=completed_at, comment=comment)
            )

            await session.commit()

            return result.rowcount > 0

    async def delete(self, task_id: str) -> None:

        async with AsyncSessionLocal() as session:

            await session.execute(
                delete(CashCollectionTaskTable).where(
                    CashCollectionTaskTable.id == task_id
                )
            )

            await session.commit()
            
    async def delete_many(self, task_ids: list[str]) -> None:
        """Удаляет несколько строк по списку id."""

        if not task_ids:
            return

        async with AsyncSessionLocal() as session:

            await session.execute(
                delete(CashCollectionTaskTable).where(
                    CashCollectionTaskTable.id.in_(task_ids)
                )
            )

            await session.commit()

    async def delete_by_parent_id(self, parent_id: str) -> None:

        async with AsyncSessionLocal() as session:

            await session.execute(
                delete(CashCollectionTaskTable).where(
                    CashCollectionTaskTable.parent_id == parent_id
                )
            )

            await session.commit()

    async def get_by_id(self, task_id: str) -> CashCollectionTaskTable | None:

        async with AsyncSessionLocal() as session:

            result = await session.execute(
                select(CashCollectionTaskTable).where(
                    CashCollectionTaskTable.id == task_id
                )
            )

            return result.scalar_one_or_none()

    async def get_all(self, is_active: bool | None = True) -> list[CashCollectionTaskTable]:
        """
        Возвращает записи, отфильтрованные по is_active.
        is_active=True  - только активные (по умолчанию)
        is_active=False - только неактивные
        is_active=None  - все записи без фильтра
        """

        query = select(CashCollectionTaskTable).order_by(
            CashCollectionTaskTable.created_at,
            CashCollectionTaskTable.id,
        )

        if is_active is not None:
            query = query.where(CashCollectionTaskTable.is_active.is_(is_active))

        async with AsyncSessionLocal() as session:

            result = await session.execute(query)

            return list(result.scalars().all())

    async def get_by_parent_id(self, parent_id: str) -> list[CashCollectionTaskTable]:

        async with AsyncSessionLocal() as session:

            result = await session.execute(
                select(CashCollectionTaskTable)
                .where(CashCollectionTaskTable.parent_id == parent_id)
                .order_by(CashCollectionTaskTable.created_at, CashCollectionTaskTable.id)
            )

            return list(result.scalars().all())

    async def get_by_performer_id(self, performer_id: int) -> list[CashCollectionTaskTable]:

        async with AsyncSessionLocal() as session:

            result = await session.execute(
                select(CashCollectionTaskTable)
                .where(CashCollectionTaskTable.performer_id == performer_id)
                .order_by(CashCollectionTaskTable.created_at, CashCollectionTaskTable.id)
            )

            return list(result.scalars().all())

    async def get_by_status(self, status: str) -> list[CashCollectionTaskTable]:

        async with AsyncSessionLocal() as session:

            result = await session.execute(
                select(CashCollectionTaskTable)
                .where(CashCollectionTaskTable.status == status)
                .order_by(CashCollectionTaskTable.created_at, CashCollectionTaskTable.id)
            )

            return list(result.scalars().all())
    
      
    async def get_completed_since(self, since: datetime) -> list[CashCollectionTaskTable]:
        """
        Возвращает строки с is_active == False и created_at >= since.
        """

        async with AsyncSessionLocal() as session:

            result = await session.execute(
                select(CashCollectionTaskTable)
                .where(
                    CashCollectionTaskTable.is_active.is_(False),
                    CashCollectionTaskTable.created_at >= since,
                )
                .order_by(
                    CashCollectionTaskTable.created_at,
                    CashCollectionTaskTable.id,
                )
            )

            return list(result.scalars().all())