from sqlalchemy import select, delete

from database.session import AsyncSessionLocal
from database.models.scheduled_task import ScheduledTaskTable
from telegram_bot.models.schedule_task import ScheduledTask


class ScheduledTaskRepository:

    # ==========================================
    # UPSERT
    # ==========================================

    async def upsert(
        self,
        task: ScheduledTask
    ) -> ScheduledTaskTable:

        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(ScheduledTaskTable).where(
                    ScheduledTaskTable.id == task.id
                )
            )

            db_task = result.scalar_one_or_none()
            # ==========================================
            # UPDATE
            # ==========================================

            if db_task:

                db_task.title = task.title
                db_task.description = task.description

                db_task.group_id = task.group_id
                db_task.topic_id = task.topic_id
                db_task.group_title = task.group_title

                db_task.creator_id = task.creator_id
                db_task.creator_name = task.creator_name

                db_task.performer_id = task.performer_id
                db_task.performer_name = task.performer_name

                db_task.priority = task.priority
                db_task.address = task.address

                db_task.task_type = task.task_type

                db_task.created_at = task.created_at

                db_task.every_n_days = task.every_n_days
                db_task.next_run_at = task.next_run_at

            # ==========================================
            # CREATE
            # ==========================================

            else:

                db_task = ScheduledTaskTable(

                    id=task.id,

                    title=task.title,
                    description=task.description,

                    group_id=task.group_id,
                    topic_id=task.topic_id,
                    group_title=task.group_title,

                    creator_id=task.creator_id,
                    creator_name=task.creator_name,

                    performer_id=task.performer_id,
                    performer_name=task.performer_name,

                    priority=task.priority,
                    address=task.address,

                    task_type=task.task_type,

                    created_at=task.created_at,

                    every_n_days=task.every_n_days,
                    next_run_at=task.next_run_at
                )

                session.add(db_task)

            await session.commit()

            return db_task

    # ==========================================
    # DELETE
    # ==========================================

    async def delete(
        self,
        task_id: str
    ) -> None:

        async with AsyncSessionLocal() as session:

            await session.execute(
                delete(ScheduledTaskTable).where(
                    ScheduledTaskTable.id == task_id
                )
            )

            await session.commit()

    # ==========================================
    # GET ALL
    # ==========================================

    async def get_all(self) -> list[ScheduledTaskTable]:

        async with AsyncSessionLocal() as session:

            result = await session.execute(
                select(ScheduledTaskTable)
            )

            return list(result.scalars().all())