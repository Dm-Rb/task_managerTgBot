from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum


class TaskStatus(Enum):
    CREATED = "Новая"
    IN_PROGRESS = "В процессе"
    COMPLETED = "Выполнено"
    CANCELLED = "Отменена"
    # CONFIG = "Конфигурация задачи по-расписанию"

    def __str__(self):
        return self.value


class TaskType(Enum):
    ONCE = "Разово"
    RECURRING = "По расписанию"

    @classmethod
    def get_by_index(cls, index: int):
        return list(cls)[index].value


class RecurrenceInterval(Enum):
    DAILY = "daily"
    EVERY_N_DAYS = "every_n_days"
    # WEEKLY = "weekly"
    # MONTHLY = "monthly"


class TaskPriority(Enum):
    NORMAL = "Обычный"
    HIGH = "Высокий"
    URGENT = "Срочный"

    @classmethod
    def get_all(cls):
        return [p.value for p in cls]

    @classmethod
    def get_by_index(cls, index: int):
        return list(cls)[index].value


@dataclass
class Task:
    # === Поля без значения по умолчанию (обязательные) ===
    task_id: str
    title: str
    description: str
    group_id: int
    group_title: str
    creator_id: int
    creator_name: str
    performer_id: int
    performer_name: str
    priority: str
    created_at: datetime

    # === Поля с значениями по умолчанию (должны быть в конце) ===

    status: TaskStatus = TaskStatus.CREATED
    task_type: TaskType = TaskType.ONCE

    accepted_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Для циклических задач
    every_n_days: Optional[int] = None

    is_active: bool = True


@dataclass
class TaskTemplate:
    title: str
    description: str








