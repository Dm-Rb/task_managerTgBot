from telegram_bot.models.task import Task, TaskTemplate, TaskStatus, TaskType
from telegram_bot.storage.task_cache import TaskCache
import datetime
from telegram_bot.storage.task_indexes import TaskIndexes
from uuid import uuid4


class TaskService:

    def __init__(self, cache: TaskCache, database):
        self.task_cache: dict[str, Task] = cache.tasks
        self.templates_cache: list[TaskTemplate] = cache.templates
        self.database = database
        self.indexes = TaskIndexes()

    def add_template(self, title: str, description: str):
        self.templates_cache.append(
            TaskTemplate(
                title=title,
                description=description
            )
        )

    def get_all_templates(self) -> list:
        return self.templates_cache

    def get_template(self, index) -> TaskTemplate or None:
        return self.templates_cache[index]

    ######################

    def get_task(self, task_id: str) -> Task or None:
        return self.task_cache.get(task_id)

    def upsert_task(self, task: Task) -> Task:
        """
        Создать или обновить задачу
        """

        existing_task = self.task_cache.get(task.task_id)
        if not existing_task:  # если нет - создать новую
            self.task_cache[task.task_id] = task

            self.indexes.register_task(task)

            return task
        self.task_cache[task.task_id] = task

        return task

    def add_task(self,
        title: str,
        description: str,
        group_id: int,
        group_title: str,
        creator_id: int,
        creator_name: str,
        performer_id: int,
        performer_name: str,
        priority: str,
        task_type: TaskType,
        created_at: datetime
    ) -> Task:
        """
        Создать и добавить задачу в cache
        """
        task_id = uuid4().hex[:16]  # генерим уникальный id
        task = Task(
            task_id=task_id,

            title=title,
            description=description,

            group_id=group_id,
            group_title=group_title,

            creator_id=creator_id,
            creator_name=creator_name,

            performer_id=performer_id,
            performer_name=performer_name,

            priority=priority,

            status=TaskStatus.CREATED,
            task_type=task_type,
            created_at=created_at
        )

        self.task_cache[task_id] = task
        self.indexes.register_task(task)
        # Добавить логику записи в базу данных в базу данных
        return task

    def remove_task(self, task_id: str):
        task = self.get_task(task_id)
        if not task:
            return
        self.indexes.remove_task(task)
        self.task_cache.pop(task_id, None)

        # Добавить логику записи в базу данных в базу данных если статус не Отменено



