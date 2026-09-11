from telegram_bot.storage.template_cache import TemplateCache
from database.models.adress import AdressTable
from database.models.task_tittle import TaskTittleTemplateTable
from database.repositories.city import CityRepository
from database.repositories.adress import AdressRepository
from database.repositories.task_tittle import TaskTittleRepository
from database.repositories.point import PointRepository
from database.models.city import CityTable
from database.models.adress import AdressTable
from database.models.point import PointTable



class TemplateService(TemplateCache):
    """Этот сервис работает с базой данных адресов и городов только нна чтение"""

    def __init__(self, task_tittle_database, city_database, adress_database, point_database):
        self.task_tittle_database: TaskTittleRepository = task_tittle_database
        self.city_database: CityRepository = city_database
        self.adress_database: AdressRepository = adress_database
        self.point_database: PointRepository = point_database
        
    
    async def warmup(self):
        """
        Прогрев кешей из базы данных
        """
        # Греем кеш для титульников. Формируем словарь где ключь - ай, значение - объект
        r: list[TaskTittleTemplateTable] = await self.task_tittle_database.get_all()
        self.tittles = {item.id: item for item in r}
        # ждём ответа бд
        cities = await self.city_database.get_all()
        adreses = await self.adress_database.get_all()
        points = await self.point_database.get_all()
        ## формируем кеш 
        self.cities: dict[int, CityTable] = {item.id: item for item in cities}
        self.adreses: dict[int, AdressTable] = {item.id: item for item in adreses}
        self.points: dict[int, PointTable] = {item.id: item for item in points}
        # Формируем строки из city + adress
        self.adress_templates = [f"{item.adress}, {self.cities[item.city_id]}" for item in adreses]

        return
    
    
    async def create_new_task_tittle(self, title: str, is_sheduler: False) -> TaskTittleTemplateTable:
        r: TaskTittleTemplateTable = await self.task_tittle_database.create(title, is_sheduler)
        self.tittles[r.id] = r
        return r

    async def get_all_task_tittles(self, dump: bool = False) -> list:
        if not self.tittles:
            r: list[TaskTittleTemplateTable] = await self.task_tittle_database.get_all()
            self.tittles = {item.id: item for item in r}
        if dump:
            result = [
                        {
                            column.name: getattr(task, column.name)
                            for column in TaskTittleTemplateTable.__table__.columns
                        }
                        for task in list(self.tittles.values())
                    ]
            return result
        return list(self.tittles.values())
    
    async def remove_task_tittle_by_id(self, id_) -> bool:
        k = self.tittles.pop(id_, None)

        if k:
            await self.task_tittle_database.delete(id_)
    
    async def remove_task_tittle_by_name(self, tiitle) -> bool:
        for k, v in self.tittles.items():
            if v.tittle == tiitle:
                self.tittles.pop(k, None)
                await self.task_tittle_database.delete(k)
                return
            
    async def update_task_tittle(self, id_: int, tiitle: str, is_sheduler: bool) -> None:
        r = await self.task_tittle_database.update(id_, tiitle, is_sheduler)
        self.tittles[id_] = r
        return

    ###
    
    async def get_all_adress_templates(self) -> list:
        if not self.adress_templates:
            cities: dict = {item.id: item.city for item in self.city_database.get_all()}
            # Далее записываем в кеш строки типа "city, adress"
            self.adress_templates = [f"{item.adress}, {cities[item.city_id]}" for item in self.adress_database.get_all()]
        return self.adress_templates
    
    async def add_adress_templates(self, adress: str) -> None:
        """ничего не пишем в бд, просто добавляем строку в кеш"""
        self.adress_templates.append(adress)
        return
    
    async def remove_adress_templates(self, adress: str) -> bool:
        """ничего не удаляем из бд, просто удаляем из кеша"""
        self.adress_templates.remove(adress)
        return
    
    def get_all_points_for_api(self) -> dict:
        """Получаем все данные связанные с точкой для отображения в браузере"""
        points = []
        adreses = []
        cities =[]
        def model_to_dict(obj):
            return {
                column.name: getattr(obj, column.name)
                for column in obj.__table__.columns
            }
        for point in self.points.values():
            points.append(model_to_dict(point))
        for adress in self.adreses.values():
            adreses.append(model_to_dict(adress))
        for city in self.cities.values():
            cities.append(model_to_dict(city))
        return {"points": points, "adreses": adreses, "cities": cities}
    
    
    async def new_city(self, city: str) -> dict:
        city = await self.city_database.create(city)
        self.cities[city.id] = city
        return {column.name: getattr(city, column.name) for column in city.__table__.columns}
    
    async def new_adress(self, adress: str, city_id: int) -> dict:
        adress = await self.adress_database.create(adress, city_id)
        self.adreses[adress.id] = adress
        return {column.name: getattr(adress, column.name) for column in adress.__table__.columns}
    
    async def new_point(self, point: str, id_device: str, city_id: int, adress_id: int) -> dict:
        point = await self.point_database.create(point, id_device, city_id, adress_id)
        self.points[point.id] = point
        return {column.name: getattr(point, column.name) for column in point.__table__.columns}
    
    async def update_city(self, id_, city: str) -> dict:
        city = await self.city_database.update(id_, city)
        self.cities[city.id] = city
        return {column.name: getattr(city, column.name) for column in city.__table__.columns}
    
    async def update_adress(self, id_, adress, city_id: str) -> dict:
        adress = await self.adress_database.update(id_, adress, city_id)
        self.adreses[adress.id] = adress
        return {column.name: getattr(adress, column.name) for column in adress.__table__.columns}
    
    async def update_point(self, id_, point: str, id_device: str, city_id: int, adress_id: int) -> dict:
        point = await self.point_database.update(id_, point, id_device, city_id, adress_id)
        self.points[point.id] = point
        return {column.name: getattr(point, column.name) for column in point.__table__.columns}
        
    async def delete_city(self, id_) -> None:
        # метод удаляет как саму запись в таблице, так и зависимые от city данные (adresses, points) 
        await self.city_database.delete(id_)
        # удаляем кеши
        del self.cities[id_]
        for key in list(self.adreses.keys()):
            if self.adreses[key].city_id == id_:                
                self.adreses.pop(key)
        for key in list(self.points.keys()):
            if self.points[key].city_id == id_:                
                self.points.pop(key)
        return
    
    async def delete_adress(self, id_) -> None:
        # метод удаляет как саму запись в таблице, так и зависимые от adress данные (points) 
        await self.adress_database.delete(id_)
        # удаляем кеши
        del self.adreses[id_]
        for key in list(self.points.keys()):
            if self.points[key].adress_id == id_:                
                self.points.pop(key)
        return
    
    async def delete_point(self, id_) -> None:
        await self.point_database.delete(id_)
        # удаляем кеши
        del self.points[id_]
        return
    