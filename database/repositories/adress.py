from sqlalchemy import delete, select

from database.session import AsyncSessionLocal
from database.models.adress import AdressTable
from database.models.point import PointTable


class AdressRepository:
    
    async def create(self, adress: str, city_id: int) -> AdressTable:

        async with AsyncSessionLocal() as session:
            template = AdressTable(
                adress=adress,
                city_id=city_id
            )

            session.add(template)
            await session.commit()
            await session.refresh(template)

            return template
        
    async def get_by_id(self, template_id: int) -> AdressTable| None:

        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(AdressTable).where(
                    AdressTable.id == template_id
                )
            )

            return result.scalar_one_or_none()

    async def get_all(self) -> list[AdressTable]:

        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(AdressTable)
            )

            return list(result.scalars().all())

    async def update(self,
                     template_id: int, 
                     adress: str,
                     city_id: int) -> AdressTable | None:

        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(AdressTable).where(
                    AdressTable.id == template_id
                )
            )

            template = result.scalar_one_or_none()

            if template is None:
                return None

            template.adress = adress
            template.city_id = city_id

            await session.commit()
            await session.refresh(template)

            return template

    async def delete(self, template_id: int) -> bool:

        async with AsyncSessionLocal() as session:

            # Сначала проверяем, существует ли адрес
            result = await session.execute(
                select(AdressTable).where(
                    AdressTable.id == template_id
                )
            )

            template = result.scalar_one_or_none()

            if template is None:
                return False

            # Удаляем все точки, связанные с адресом
            await session.execute(
                delete(PointTable).where(
                    PointTable.adress_id == template_id
                )
            )

            # Удаляем сам адрес
            await session.delete(template)

            await session.commit()

            return True