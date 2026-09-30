from telegram_bot.storage.cash_collection_cache import CashCollectionCache

from telegram_bot.models.cash_collection_task import (
    ScheduledCashCollectionTask, 
    CashCollectionTask, 
    CashCollectionPoint
)
from telegram_bot.models.cash_collection_task import (
    ScheduledCashCollectionTask, 
    CashCollectionTask, 
    CashCollectionPoint
)

from database.repositories.cash_collection_shedule_task import CashCollectionScheduleTaskRepository
from database.repositories.cash_collection_task import CashCollectionTaskRepository
from database.models.cash_colletrion_task import CashCollectionTaskTable
from telegram_bot.services.template_service import TemplateService
import datetime
from uuid import uuid4
from dataclasses import replace
from collections import defaultdict
from dataclasses import asdict



class CashCollectionService(CashCollectionCache):

    def __init__(self, shedule_task_database, task_database, template_service):
        self.shedule_task_database: CashCollectionScheduleTaskRepository = shedule_task_database
        self.task_database: CashCollectionTaskRepository = task_database
        self.template_service: TemplateService = template_service
        
    async def warmup(self):
        # расписания
        db_shedule_tasks = await self.shedule_task_database.get_all()

        self.sheduled_tasks = {
            db_task.id: ScheduledCashCollectionTask(
                id=db_task.id,
                city_id=db_task.city_id,
                city=db_task.city,
                description=db_task.description,
                creator_id=db_task.creator_id,
                creator_name=db_task.creator_name,
                performer_id=db_task.performer_id,
                performer_name=db_task.performer_name,
                created_at=db_task.created_at,
                every_n_days=db_task.every_n_days,
                next_run_at=db_task.next_run_at,
            )
            for db_task in db_shedule_tasks
        }
        # задачи 
        db_tasks = await self.task_database.get_all(True)
        # группируем задачи по parent_id
        groups: dict[str, list] = defaultdict(list)
        for row in db_tasks:
            groups[row.parent_id].append(row)
        # создаём экземпляры и пишем в кеш
        self.tasks = {
            parent_id: CashCollectionTask(
                parent_id=parent_id,
                city_id=group[0].city_id,
                city=group[0].city,
                description=group[0].description,
                creator_id=group[0].creator_id,
                creator_name=group[0].creator_name,
                performer_id=group[0].performer_id,
                performer_name=group[0].performer_name,
                created_at=group[0].created_at,
                points=[
                    CashCollectionPoint(
                        id=row.id,
                        adress_id=row.adress_id,
                        adress=row.adress,
                        point_id=row.point_id,
                        point=row.point,
                        id_device=row.id_device,
                        status=row.status,
                        comment=row.comment,
                        completed_at=row.completed_at,
                    )
                    for row in group
                ],
            )
            for parent_id, group in groups.items()
        }
        return
        
        
    async def create_shedule_task(self, 
                              city_id: int,
                              city: str,
                              description: str,
                              creator_id: int,
                              creator_name: str,
                              performer_id: int,
                              performer_name: str,
                              every_n_days: int
                            )->ScheduledCashCollectionTask:
        
        id_ = uuid4().hex[:16]  # генерим уникальный id
        created_at = datetime.datetime.now()
        sheduled_task = ScheduledCashCollectionTask(
                    id=id_,
                    city_id=city_id,
                    city=city,
                    description=description,
                    creator_id=creator_id,
                    creator_name=creator_name,
                    performer_id=performer_id,
                    performer_name=performer_name,
                    created_at=created_at.replace(second=0, microsecond=0),
                    every_n_days=every_n_days,
                    next_run_at = created_at.replace(second=0, microsecond=0)
                )

        self.sheduled_tasks[id_ ] = sheduled_task # add to csh
        # запись в базу данных
        await self.shedule_task_database.upsert(sheduled_task)        
        return sheduled_task
    
    async def get_shedule_tasks(self)->list[ScheduledCashCollectionTask]:        
        return list(self.sheduled_tasks.values())
    
    async def remove_shedule_task_by_id(self, shedule_task_id)->list[ScheduledCashCollectionTask]:        
        del self.sheduled_tasks[shedule_task_id]
        await self.shedule_task_database.delete(shedule_task_id)
        return
    
    async def create_task(
        self,
        schedule_task: ScheduledCashCollectionTask
        ) -> CashCollectionTask:
        """
        Создаёт CashCollectionTask по расписанию и записывает в БД
        по одной строке на каждую точку города.
        """

        # одно значение времени на все строки задачи (по нему группируем при чтении)
        created_at = datetime.datetime.now().replace(second=0, microsecond=0)
        # точки города, для которого создано расписание
        points = [
            CashCollectionPoint(
                id=uuid4().hex[:16],
                adress_id=point_obj.adress_id,
                adress=self.template_service.adreses[point_obj.adress_id].adress,
                point_id=point_obj.id,
                point=point_obj.point,
                id_device=point_obj.id_device,
                status="В процессе"
            )
            for point_obj in self.template_service.points.values()
            if point_obj.city_id == schedule_task.city_id # фильтруем по city_id
        ]
        if not points:
            raise ValueError(f"Нет точек для города {schedule_task.city} (id={schedule_task.city_id})")
        task = CashCollectionTask(
            parent_id=schedule_task.id,
            city_id=schedule_task.city_id,
            city=schedule_task.city,
            description=schedule_task.description,
            creator_id=schedule_task.creator_id,
            creator_name=schedule_task.creator_name,
            performer_id=schedule_task.performer_id,
            performer_name=schedule_task.performer_name,
            created_at=created_at,
            points=points,
        ) 
        # сдвигаем расписание
        delta = datetime.timedelta(days=schedule_task.every_n_days)
        next_run_at = schedule_task.next_run_at + delta
        now = datetime.datetime.now()
        if next_run_at <= now:
            next_run_at = now + delta
            
        updated_schedule = replace(schedule_task, next_run_at=next_run_at)
        
        # строки предыдущего запуска (берём из кеша ДО его перезаписи)
        old_task = self.tasks.get(schedule_task.id)
        if old_task:
            for old_point in old_task.points:
                old_point.is_active = False
                if old_point.completed_at is None:
                    old_point.status = "Не выполнено"

            old_rows = old_task.tasks_to_rows()
        else:
            old_rows = []

        # одна транзакция: старые строки + новые строки
        await self.task_database.upsert_many(old_rows + task.tasks_to_rows())
        await self.shedule_task_database.upsert(updated_schedule)

        # записываем в кеш
        self.sheduled_tasks[schedule_task.id] = updated_schedule
        self.tasks[schedule_task.id] = task
        return task
    
    async def remove_task(self, parent_id: str) -> None:
        """
        Удаляет из БД точки задачи со статусом "В процессе".
        Точки со статусом "Готово" не трогает.
        Удаляет задачу из кеша.
        """

        task = self.tasks.get(parent_id)
        if task is None:
            raise ValueError(f"Задача с parent_id={parent_id} не найдена в кеше")

        ids_to_delete = [
            point.id for point in task.points
            if point.status == "В процессе"
        ]

        await self.task_database.delete_many(ids_to_delete)

        del self.tasks[parent_id]

    async def sync_point(self, task: CashCollectionTask, point: CashCollectionPoint) -> None:
        """Записывает точку в БД: общие поля задачи + все текущие поля точки."""
        common = asdict(task)
        common.pop("points", None)
        row = {**common, **asdict(point)}
        await self.task_database.upsert(row)
        
    async def get_completed_tasks(self, days: int = 30) -> list[CashCollectionTaskTable]:
        """
        Возвращает строки (is_active == False), созданные за последние `days` дней.
        Используется для формирования CSV-отчёта, группировка не нужна.
        """

        since = datetime.datetime.now() - datetime.timedelta(days=days)
        return await self.task_database.get_completed_since(since)