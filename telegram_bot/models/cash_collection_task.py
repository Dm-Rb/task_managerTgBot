from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional
from telegram_bot.models.task import TaskType


@dataclass
class ScheduledCashCollectionTask:
    id: str
    city_id: int
    city: str
    description: str
    creator_id: int
    creator_name: str
    performer_id: int
    performer_name: str
    created_at: datetime
    # Раз в сколько дней создавать задачу
    every_n_days:  Optional[int] = None
    # Создать задачу в:
    next_run_at: Optional[datetime] = None

@dataclass
class CashCollectionPoint:
    id: str
    adress_id: int
    adress: str
    point_id: int
    point: str
    id_device: str    
    status: str
    completed_at: Optional[datetime] = None
    comment: Optional[str] = None
    file_id_before: Optional[str] = None
    file_id_after: Optional[str] = None
    is_active: bool = True

 
@dataclass
class CashCollectionTask:
    parent_id: str # ScheduledCashCollectionTask.id
    city_id: int
    city: str
    description: str
    creator_id: int
    creator_name: str
    performer_id: int
    performer_name: str
    created_at: datetime
    points : list[CashCollectionPoint]
    
    def tasks_to_rows(self) -> list[dict]:
        """Одна строка (словарь) на каждую точку: поля задачи + поля точки."""
        common = asdict(self) # рекурсивно превращает датакласс и вложенные CashCollectionPoint в словари
        points = common.pop("points")   # превращает список точек в словарь и отделяет от общих полей
        return [{**common, **point} for point in points]
    