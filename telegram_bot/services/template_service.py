from telegram_bot.storage.template_cache import TemplateCache
from database.models.adress import AdressTable
from database.models.task_tittle import TaskTittleTemplateTable
from database.repositories.city import CityRepository

from database.repositories.adress import AdressRepository
from database.repositories.task_tittle import TaskTittleRepository


class TemplateService(TemplateCache):
    """Этот сервис работает с базой данных адресов и городов только нна чтение"""

    def __init__(self, task_tittle_database, city_database, adress_database):
        self.task_tittle_database: TaskTittleRepository = task_tittle_database
        self.city_database: CityRepository = city_database
        self.adress_database: AdressRepository = adress_database
        
    
    async def warmup(self):
        """
        Прогрев кешей из базы данных
        """
        # Греем кеш для титульников. Формируем словарь где ключь - ай, значение - объект
        r: list[TaskTittleTemplateTable] = await self.task_tittle_database.get_all()
        self.tittles = {item.id: item for item in r}
        # Греем кеш для адресов. Формируем строки из city + adress
        # сперва города {id: city}
        cities = await self.city_database.get_all()
        cities: dict = {item.id: item.city for item in cities}
        # Далее записываем в кеш строки типа "city, adress"
        adresses = await self.adress_database.get_all()
        self.adresses = [f"{item.adress}, {cities[item.city_id]}" for item in adresses]

        return
    
    
    async def add_task_tittle(self, title: str, is_sheduler: False) -> None:
        r: TaskTittleTemplateTable = await self.task_tittle_database.create(title, is_sheduler)
        self.tittles[r.id] = r
        return

    async def get_all_task_tittles(self) -> list:
        if not self.tittles:
            r: list[TaskTittleTemplateTable] = await self.task_tittle_database.get_all()
            self.tittles = {item.id: item for item in r}
        return list(self.tittles.values())
    
    async def remove_task_tittle_by_id(self, id_) -> bool:
        k = self.tittles.pop(id_, None)

        if k:
            await self.task_tittle_database.delete(k)
    
    async def remove_task_tittle_by_name(self, tiitle) -> bool:
        for k, v in self.tittles.items():
            if v.tittle == tiitle:
                self.tittles.pop(k, None)
                await self.task_tittle_database.delete(k)
                return
    ###
    
    async def get_all_adresses(self) -> list:
        if not self.adresses:
            cities: dict = {item.id: item.city for item in self.city_database.get_all()}
            # Далее записываем в кеш строки типа "city, adress"
            self.adresses = [f"{item.adress}, {cities[item.city_id]}" for item in self.adress_database.get_all()]
        return self.adresses
    
    async def add_adress(self, adress: str) -> None:
        """ничего не пишем в бд, просто добавляем строку в кеш"""
        self.adresses.append(adress)
        return
    async def remove_adress(self, adress: str) -> bool:
        """ничего не удаляем из бд, просто удаляем из кеша"""
        self.adresses.remove(adress)
        return