from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from telegram_bot.models.task import TaskType


@dataclass
class ScheduledTask:
    id: str
    title: str
    description: str
    group_id: int
    topic_id: int or None
    group_title: str  # если есть топик в группе > group.title + ' / ' + topic.title
    creator_id: int
    creator_name: str
    performer_id: int
    performer_name: str
    priority: str
    address: str or None
    priority: str
    created_at: datetime
    task_type: TaskType = TaskType.RECURRING

    # Раз в сколько дней создавать задачу
    every_n_days:  Optional[int] = None
    # Создать задачу в:
    next_run_at: Optional[datetime] = None
