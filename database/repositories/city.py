from sqlalchemy import delete, select
from database.session import AsyncSessionLocal
from database.models.city import CityTable


class CityRepository:

    async def create(self, city: str) -> CityTable:

        async with AsyncSessionLocal() as session:
            template = CityTable(
                city=city,
            )

            session.add(template)
            await session.commit()
            await session.refresh(template)

            return template

    async def get_by_id(self, template_id: int) -> CityTable | None:

        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(CityTable).where(
                    CityTable.id == template_id
                )
            )

            return result.scalar_one_or_none()

    async def get_all(self) -> list[CityTable]:

        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(CityTable)
            )

            return list(result.scalars().all())

    async def update(
        self,
        template_id: int,
        city: str
    ) -> CityTable | None:

        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(CityTable).where(
                    CityTable.id == template_id
                )
            )

            template = result.scalar_one_or_none()

            if template is None:
                return None

            template.city = city

            await session.commit()
            await session.refresh(template)

            return template

    async def delete(self, template_id: int) -> bool:

        async with AsyncSessionLocal() as session:
            result = await session.execute(
                delete(CityTable).where(
                    CityTable.id == template_id
                )
            )

            await session.commit()

            return result.rowcount > 0