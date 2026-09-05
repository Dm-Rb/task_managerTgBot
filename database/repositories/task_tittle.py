from sqlalchemy import delete, select
from database.session import AsyncSessionLocal
from database.models.task_tittle import TaskTittleTemplateTable


class TaskTittleRepository:

    async def create(self, tittle: str, is_sheduler: bool = False) -> TaskTittleTemplateTable:

        async with AsyncSessionLocal() as session:
            template = TaskTittleTemplateTable(
                tittle=tittle,
                is_sheduler=is_sheduler,
            )

            session.add(template)
            await session.commit()
            await session.refresh(template)

            return template

    async def get_by_id(self, template_id: int) -> TaskTittleTemplateTable | None:

        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(TaskTittleTemplateTable).where(
                    TaskTittleTemplateTable.id == template_id
                )
            )

            return result.scalar_one_or_none()

    async def get_all(self) -> list[TaskTittleTemplateTable]:

        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(TaskTittleTemplateTable)
            )

            return list(result.scalars().all())

    async def update(self, template_id: int, tittle: str, is_sheduler: bool) -> TaskTittleTemplateTable | None:

        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(TaskTittleTemplateTable).where(
                    TaskTittleTemplateTable.id == template_id
                )
            )

            template = result.scalar_one_or_none()

            if template is None:
                return None

            template.tittle = tittle
            template.is_sheduler = is_sheduler

            await session.commit()
            await session.refresh(template)

            return template

    async def delete(self, template_id: int) -> bool:

        async with AsyncSessionLocal() as session:
            result = await session.execute(
                delete(TaskTittleTemplateTable).where(
                    TaskTittleTemplateTable.id == template_id
                )
            )

            await session.commit()

            return result.rowcount > 0

