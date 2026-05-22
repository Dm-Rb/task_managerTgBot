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

    # ==========================================
    # SCHEDULE
    # ==========================================

    every_n_days:  Optional[int] = None
    """
    Раз в сколько дней создавать задачу
    """

    # start_at: Optional[datetime] = None
    # """
    # Отложенный запуск.
    # Пока дата не наступила —
    # scheduler игнорирует задачу.
    # """

    next_run_at: Optional[datetime] = None
    """
    Когда scheduler должен
    создать следующую задачу
    """

    last_run_at: Optional[datetime] = None
    """
    Когда последний раз
    была создана задача
    """

