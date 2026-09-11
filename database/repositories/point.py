from sqlalchemy import delete, select

from database.session import AsyncSessionLocal
from database.models.point import PointTable


class PointRepository:

    async def create(self, point: str, id_device: str, city_id: int, adress_id: int) -> PointTable:

        async with AsyncSessionLocal() as session:
            template = PointTable(
                point=point,
                id_device=id_device,
                city_id=city_id,
                adress_id=adress_id,
            )

            session.add(template)
            await session.commit()
            await session.refresh(template)

            return template

    async def get_by_id(self, template_id: int) -> PointTable | None:

        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(PointTable).where(
                    PointTable.id == template_id
                )
            )

            return result.scalar_one_or_none()

    async def get_all(self) -> list[PointTable]:

        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(PointTable)
            )

            return list(result.scalars().all())

    async def update(self,
        id_: int,
        point: str,
        id_device: str,
        city_id: int,
        adress_id: int,
    ) -> PointTable | None:

        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(PointTable).where(
                    PointTable.id == id_
                )
            )

            template = result.scalar_one_or_none()

            if template is None:
                return None

            template.point = point
            template.id_device = id_device
            template.city_id = city_id
            template.adress_id = adress_id

            await session.commit()
            await session.refresh(template)

            return template

    async def delete(self, template_id: int) -> bool:

        async with AsyncSessionLocal() as session:
            result = await session.execute(
                delete(PointTable).where(
                    PointTable.id == template_id
                )
            )

            await session.commit()

            return result.rowcount > 0
        
    async def get_all_by_city_id(self, city_id: int) -> list[PointTable]:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(PointTable).where(
                    PointTable.city_id == city_id
                )
            )

            return list(result.scalars().all())

    async def get_all_by_adress_id(self, adress_id: int) -> list[PointTable]:

        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(PointTable).where(
                    PointTable.adress_id == adress_id
                )
            )

            return list(result.scalars().all())