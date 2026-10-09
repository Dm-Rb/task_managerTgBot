from database.models.task_tittle import TaskTittleTemplateTable
from database.models.city import CityTable
from database.models.adress import AdressTable
from database.models.point import PointTable



class TemplateCache:

    tittles: dict[int, TaskTittleTemplateTable] or dict = {}
    cities: dict[int, CityTable] or dict = {}
    adreses: dict[int, AdressTable] or dict = {}
    points: dict[int, PointTable] or dict = {}




