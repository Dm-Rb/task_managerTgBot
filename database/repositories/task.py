from datetime import datetime, timedelta
from sqlalchemy import (
    select,
    delete,
    distinct
)
from database.session import AsyncSessionLocal
from database.models.task import TaskTable
from telegram_bot.models.task import Task


class TaskRepository:

    # =====================================================
    # UPSERT
    # =====================================================

    @staticmethod
    def _enum_to_value(value):
        """
        Если Enum -> возвращает .value
        Если уже str/int -> возвращает как есть
        """
        return getattr(value, "value", value)

    @staticmethod
    def _normalize_datetime(dt: datetime or None):
        """
        Убираем timezone, чтобы SQLite не ломался
        """
        if dt is None:
            return None

        if dt.tzinfo is not None:
            return dt.replace(tzinfo=None)

        return dt

    async def upsert(self, task: Task) -> TaskTable:

        async with AsyncSessionLocal() as session:

            result = await session.execute(
                select(TaskTable).where(
                    TaskTable.task_id == task.task_id
                )
            )

            db_task = result.scalar_one_or_none()

            data = {

                "title": task.title,
                "description": task.description,

                "group_id": task.group_id,
                "topic_id": task.topic_id,
                "group_title": task.group_title,

                "creator_id": task.creator_id,
                "creator_name": task.creator_name,

                "performer_id": task.performer_id,
                "performer_name": task.performer_name,

                "priority": self._enum_to_value(task.priority),
                "status": self._enum_to_value(task.status),
                "task_type": self._enum_to_value(task.task_type),

                "created_at": self._normalize_datetime(task.created_at),
                "accepted_at": self._normalize_datetime(task.accepted_at),
                "completed_at": self._normalize_datetime(task.completed_at),

                "is_active": task.is_active
            }

            # ==========================================
            # UPDATE
            # ==========================================

            if db_task:

                for key, value in data.items():
                    setattr(db_task, key, value)

            # ==========================================
            # CREATE
            # ==========================================

            else:

                db_task = TaskTable(
                    task_id=task.task_id,
                    **data
                )

                session.add(db_task)

            await session.commit()
            await session.refresh(db_task)

            return db_task

    # =====================================================
    # DELETE
    # =====================================================

    async def delete(self, task_id: str) -> None:

        async with AsyncSessionLocal() as session:

            await session.execute(
                delete(TaskTable).where(
                    TaskTable.task_id == task_id
                )
            )

            await session.commit()

    # =====================================================
    # UNIQUE TITLE + DESCRIPTION
    # =====================================================

    async def get_unique_titles_descriptions(
        self
    ) -> list[tuple[str, str]]:

        async with AsyncSessionLocal() as session:

            result = await session.execute(
                select(
                    distinct(TaskTable.title),
                    TaskTable.description
                )
            )

            return list(result.all())

    # =====================================================
    # UNIQUE ADDRESSES
    # =====================================================

    async def get_unique_addresses(
        self
    ) -> list[str]:

        async with AsyncSessionLocal() as session:

            result = await session.execute(
                select(
                    distinct(TaskTable.address)
                ).where(
                    TaskTable.address.is_not(None)
                )
            )
            return [
                row[0]
                for row in result.all()
            ]

    # =====================================================
    # ACTIVE TASKS
    # =====================================================

    async def get_active_tasks(self) -> list[TaskTable]:

        async with AsyncSessionLocal() as session:

            result = await session.execute(
                select(TaskTable).where(
                    TaskTable.is_active == True
                )
            )

            return list(result.scalars().all())

    # =====================================================
    # COMPLETED TASKS (30 DAYS)
    # =====================================================

    async def get_completed_tasks_last_30_days(
        self
    ) -> list[TaskTable]:

        async with AsyncSessionLocal() as session:

            date_from = datetime.now() - timedelta(days=30)

            result = await session.execute(
                select(TaskTable).where(
                    TaskTable.is_active == False,
                    TaskTable.created_at >= date_from
                )
            )

            return list(result.scalars().all())