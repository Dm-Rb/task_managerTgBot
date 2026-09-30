from sqlalchemy import delete, select

from database.session import AsyncSessionLocal
from database.models.cash_collection_shedule_task import CashCollectionSheduleTaskTable
from telegram_bot.models.cash_collection_task import ScheduledCashCollectionTask


class CashCollectionScheduleTaskRepository:

    async def upsert(self, task: ScheduledCashCollectionTask) -> CashCollectionSheduleTaskTable:
        
        async with AsyncSessionLocal() as session:

            result = await session.execute(
                select(CashCollectionSheduleTaskTable).where(
                    CashCollectionSheduleTaskTable.id == task.id
                )
            )

            db_task = result.scalar_one_or_none()

            # UPDATE
            if db_task:

                db_task.city_id = task.city_id
                db_task.city = task.city

                db_task.description = task.description

                db_task.creator_id = task.creator_id
                db_task.creator_name = task.creator_name

                db_task.performer_id = task.performer_id
                db_task.performer_name = task.performer_name

                db_task.created_at = task.created_at

                db_task.every_n_days = task.every_n_days
                db_task.next_run_at = task.next_run_at

            # CREATE
            else:

                db_task = CashCollectionSheduleTaskTable(

                    id=task.id,

                    city_id=task.city_id,
                    city=task.city,

                    description=task.description,

                    creator_id=task.creator_id,
                    creator_name=task.creator_name,

                    performer_id=task.performer_id,
                    performer_name=task.performer_name,

                    created_at=task.created_at,

                    every_n_days=task.every_n_days,
                    next_run_at=task.next_run_at,
                )

                session.add(db_task)

            await session.commit()

            return db_task
        
    async def delete(self, task_id: str) -> None:

        async with AsyncSessionLocal() as session:

            await session.execute(
                delete(CashCollectionSheduleTaskTable).where(
                    CashCollectionSheduleTaskTable.id == task_id
                )
            )

            await session.commit()

    async def get_by_id(self, task_id: str) -> CashCollectionSheduleTaskTable | None:

        async with AsyncSessionLocal() as session:

            result = await session.execute(
                select(CashCollectionSheduleTaskTable).where(
                    CashCollectionSheduleTaskTable.id == task_id
                )
            )

            return result.scalar_one_or_none()

    async def get_all(self) -> list[CashCollectionSheduleTaskTable]:

        async with AsyncSessionLocal() as session:

            result = await session.execute(
                select(CashCollectionSheduleTaskTable)
            )

            return list(result.scalars().all())
