from database.models.task_tittle import TaskTittleTemplateTable
from database.models.city import CityTable
from database.models.adress import AdressTable
from database.models.point import PointTable



class TemplateCache:

    tittles: dict[int, TaskTittleTemplateTable] or dict = {}
    adress_templates: list[str] or list = [] # этот список хранит строки шаблонов для модуля создания задач
    cities: dict[int, CityTable] or dict = {}
    adreses: dict[int, AdressTable] or dict = {}
    points: dict[int, PointTable] or dict = {}




