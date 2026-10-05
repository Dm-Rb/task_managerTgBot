from datetime import datetime
from sqlalchemy import delete, desc, func, select
from database.models.sms_logs import SmsTable 
from database.session import AsyncSessionLocal


class SmsRepository:

    async def get_all(self) -> list[SmsTable]:

        async with AsyncSessionLocal() as session:

            result = await session.execute(
                select(SmsTable).order_by(SmsTable.completed_at.desc())
            )

            return list(result.scalars().all())

    async def delete_by_id(self, sms_id: int) -> None:

        async with AsyncSessionLocal() as session:

            await session.execute(
                delete(SmsTable).where(SmsTable.id == sms_id)
            )

            await session.commit()

    async def get_page(self, offset: int = 0, limit: int = 10) -> list[SmsTable]:
        """
        Пагинация: возвращает `limit` записей начиная с `offset`,
        отсортированные от самых новых к самым старым.
        """

        async with AsyncSessionLocal() as session:

            result = await session.execute(
                select(SmsTable)
                .order_by(SmsTable.completed_at.desc())
                .offset(offset)
                .limit(limit)
            )

            return list(result.scalars().all())

    async def get_latest(self, limit: int = 10) -> list[SmsTable]:
        """Первые `limit` записей по самой свежей дате (completed_at)."""

        async with AsyncSessionLocal() as session:

            result = await session.execute(
                select(SmsTable)
                .order_by(SmsTable.completed_at.desc())
                .limit(limit)
            )

            return list(result.scalars().all())
        
    async def create(self, from_: str, text: str, sent_stamp: str, completed_at: datetime) -> SmsTable:
        """Записывает новое входящее СМС."""

        async with AsyncSessionLocal() as session:

            sms = SmsTable(
                from_=from_,
                text=text,
                sentStamp=sent_stamp,
                completed_at=completed_at,
            )

            session.add(sms)
            await session.commit()
            await session.refresh(sms)

            return sms

    async def count(self) -> int:
        """Общее количество записей — пригодится для расчёта числа страниц."""

        async with AsyncSessionLocal() as session:

            result = await session.execute(
                select(func.count()).select_from(SmsTable)
            )

            return result.scalar_one()
        

        
