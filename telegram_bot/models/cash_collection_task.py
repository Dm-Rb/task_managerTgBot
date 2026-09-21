from dataclasses import dataclass, field
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
class CashCollectionTask:
    id: str
    description: str
    creator_id: int
    creator_name: str
    performer_id: int
    performer_name: str
    city_id: int
    adress_id: int
    point_id: int
    created_at: datetime
    # Раз в сколько дней создавать задачу
