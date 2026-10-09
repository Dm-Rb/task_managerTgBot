from datetime import datetime
from sqlalchemy import func, select, delete
from database.models.call_logs import CallTable
from database.session import AsyncSessionLocal


class CallRepository:

    async def create(
        self,
        from_: str,
        short_text: str,
        text: str,
        completed_at: datetime,
        to_: str | None = None,
    ) -> CallTable:
        """Записывает новую запись о звонке."""

        async with AsyncSessionLocal() as session:

            call = CallTable(
                from_=from_,
                to_=to_,
                short_text=short_text,
                text=text,
                completed_at=completed_at,
            )

            session.add(call)
            await session.commit()
            await session.refresh(call)

            return call

    async def get_all(self) -> list[CallTable]:

        async with AsyncSessionLocal() as session:

            result = await session.execute(
                select(CallTable).order_by(CallTable.completed_at.desc())
            )

            return list(result.scalars().all())

    async def delete_by_id(self, call_id: int) -> None:

        async with AsyncSessionLocal() as session:

            await session.execute(
                delete(CallTable).where(CallTable.id == call_id)
            )

            await session.commit()

    async def get_page(self, offset: int = 0, limit: int = 10) -> list[CallTable]:
        """
        Пагинация: возвращает `limit` записей начиная с `offset`,
        отсортированные от самых новых к самым старым.
        """

        async with AsyncSessionLocal() as session:

            result = await session.execute(
                select(CallTable)
                .order_by(CallTable.completed_at.desc())
                .offset(offset)
                .limit(limit)
            )

            return list(result.scalars().all())

    async def count(self) -> int:
        """Общее количество записей — для расчёта числа страниц при пагинации."""

        async with AsyncSessionLocal() as session:

            result = await session.execute(
                select(func.count()).select_from(CallTable)
            )

            return result.scalar_one()
        
    async def update_by_id(
        self,
        call_id: int,
        from_: str | None = None,
        to_: str | None = None,
        short_text: str | None = None,
        text: str | None = None,
        completed_at: datetime | None = None,
        ) -> CallTable | None:
        """
        Обновляет переданные поля записи по id. Поля, которые не передали
        (остались None), не изменяются. Возвращает обновлённый объект,
        либо None, если записи с таким id нет.
        """

        async with AsyncSessionLocal() as session:

            call = await session.get(CallTable, call_id)

            if call is None:
                return None

            if from_ is not None:
                call.from_ = from_
            if to_ is not None:
                call.to_ = to_
            if short_text is not None:
                call.short_text = short_text
            if text is not None:
                call.text = text
            if completed_at is not None:
                call.completed_at = completed_at

            await session.commit()
            await session.refresh(call)

            return call