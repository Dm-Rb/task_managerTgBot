from sqlalchemy import (
    select,
    update,
    delete
)

from database.session import AsyncSessionLocal
from database.models.task import TaskTable


class TaskRepository:

    # ==========================================
    # CREATE
    # ==========================================

    async def create(
        self,
        **task_data
    ) -> TaskTable:
        """
        Создать новую задачу
        """

        async with AsyncSessionLocal() as session:

            task = TaskTable(**task_data)

            session.add(task)

            await session.commit()

            await session.refresh(task)

            return task

    # ==========================================
    # UPDATE
    # ==========================================

    async def update_by_task_id(
        self,
        task_id: str,
        **fields
    ) -> bool:
        """
        Обновить задачу по task_id
        """

        async with AsyncSessionLocal() as session:

            stmt = (
                update(TaskTable)
                .where(TaskTable.task_id == task_id)
                .values(**fields)
            )

            result = await session.execute(stmt)

            await session.commit()

            return result.rowcount > 0

    # ==========================================
    # GET COMPLETED INACTIVE
    # ==========================================

    async def get_completed_inactive_tasks(
        self
    ) -> list[TaskTable]:
        """
        Получить все завершённые неактивные задачи
        """

        async with AsyncSessionLocal() as session:

            stmt = (
                select(TaskTable)
                .where(
                    TaskTable.is_active == False,
                    TaskTable.status == "Выполнено"
                )
            )

            result = await session.execute(stmt)

            return result.scalars().all()

    # ==========================================
    # DELETE
    # ==========================================

    async def delete_by_task_id(
        self,
        task_id: str
    ) -> bool:
        """
        Удалить задачу по task_id
        """

        async with AsyncSessionLocal() as session:

            stmt = (
                delete(TaskTable)
                .where(TaskTable.task_id == task_id)
            )

            result = await session.execute(stmt)

            await session.commit()

            return result.rowcount > 0