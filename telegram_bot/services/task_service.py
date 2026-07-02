from telegram_bot.models.task import Task, TaskTemplate, TaskStatus, TaskType, AddressTemplate
from telegram_bot.models.schedule_task import ScheduledTask

from telegram_bot.storage.task_cache import TaskCache
import datetime
from telegram_bot.storage.task_indexes import TaskIndexes
from uuid import uuid4


class TaskService:

    def __init__(self, cache: TaskCache, task_database, scheduled_task_database):
        self.task_cache: dict[str, Task] = cache.tasks
        self.task_templates_cache: list[TaskTemplate] = cache.task_templates
        self.address_templates_cache: list[AddressTemplate] = cache.address_templates
        self.task_database = task_database
        self.scheduled_task_database = scheduled_task_database
        self.indexes = TaskIndexes()
        self.scheduler_task_cache: dict[str, ScheduledTask] = cache.schedule

    async def warmup(self):
        """
        Прогрев кешей из базы данных
        """

        # ==========================================
        # TASK CACHE
        # ==========================================

        self.task_cache.clear()

        active_tasks = await self.task_database.get_active_tasks()

        for row in active_tasks:
            task = Task(
                task_id=row.task_id,
                title=row.title,
                description=row.description,

                group_id=row.group_id,
                topic_id=row.topic_id,
                group_title=row.group_title,

                creator_id=row.creator_id,
                creator_name=row.creator_name,

                performer_id=row.performer_id,
                performer_name=row.performer_name,

                priority=row.priority,

                status=TaskStatus(row.status),
                task_type=TaskType(row.task_type),

                address=row.address,

                created_at=row.created_at,
                accepted_at=row.accepted_at,
                completed_at=row.completed_at,

                is_active=row.is_active
            )

            self.task_cache[task.task_id] = task

        # ==========================================
        # INDEXES
        # ==========================================

        self.indexes = TaskIndexes()

        for task in self.task_cache.values():
            self.indexes.register_task(task)

        # ==========================================
        # TASK TEMPLATES CACHE
        # ==========================================

        self.task_templates_cache.clear()

        unique_pairs = await self.task_database.get_unique_titles_descriptions()

        for title, description in unique_pairs:
            template = TaskTemplate(
                title=title,
                description=description
            )

            self.task_templates_cache.append(template)

        # ==========================================
        # ADDRESS TEMPLATES CACHE
        # ==========================================

        self.address_templates_cache.clear()

        unique_addresses = await self.task_database.get_unique_addresses()

        for address in unique_addresses:

            if not address:
                continue

            template = AddressTemplate(
                address=address
            )

            self.address_templates_cache.append(template)

        # ==========================================
        # SCHEDULED TASK CACHE
        # ==========================================

        self.scheduler_task_cache.clear()

        scheduled_tasks = await self.scheduled_task_database.get_all()

        for row in scheduled_tasks:
            scheduled_task = ScheduledTask(

                id=row.id,
                title=row.title,
                description=row.description,

                group_id=row.group_id,
                topic_id=row.topic_id,
                group_title=row.group_title,

                creator_id=row.creator_id,
                creator_name=row.creator_name,

                performer_id=row.performer_id,
                performer_name=row.performer_name,

                priority=row.priority,
                address=row.address,

                created_at=row.created_at,

                task_type=row.task_type,

                every_n_days=row.every_n_days,
                next_run_at=row.next_run_at
            )

            self.scheduler_task_cache[scheduled_task.id] = scheduled_task

    def add_task_template(self, title: str, description: str):
        self.task_templates_cache.append(
            TaskTemplate(
                title=title,
                description=description
            )
        )

    def get_all_task_templates(self) -> list:
        return self.task_templates_cache

    def get_task_template(self, index) -> TaskTemplate or None:
        return self.task_templates_cache[index]

    def remove_task_template(self, title: str, description: str) -> bool:
        """
        Удаляет шаблон адреса по значению address
        """

        for template in self.task_templates_cache:

            if template.title == title and template.description == description:
                self.task_templates_cache.remove(template)
                return True

        return False

    # адреса

    def add_address_template(self, address: str):

        self.address_templates_cache.append(
            AddressTemplate(address=address)
        )

    def get_all_address_templates(self):

        return self.address_templates_cache

    def remove_address_template(self, address: str) -> bool:
        """
        Удаляет шаблон адреса по значению address
        """

        for template in self.address_templates_cache:

            if template.address == address:
                self.address_templates_cache.remove(template)
                return True

        return False

    ######################

    def get_task(self, task_id: str) -> Task or None:
        return self.task_cache.get(task_id)

    async def upsert_task(self, task: Task) -> Task:
        """
        Создать или обновить задачу
        """

        existing_task = self.task_cache.get(task.task_id)
        if not existing_task:  # если нет - создать новую
            self.task_cache[task.task_id] = task
            self.indexes.register_task(task)
            return task
        self.task_cache[task.task_id] = task
        await self.task_database.upsert(task)
        return task

    async def add_task(self,
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
        address: str or None = None,
        topic_id: int or None = None,
        file_id: str or None = None
    ) -> Task:
        """
        Создать и добавить задачу в cache
        """
        task_id = uuid4().hex[:16]  # генерим уникальный id
        created_at = datetime.datetime.now()
        task = Task(
            task_id=task_id,
            title=title,
            description=description,
            address=address,
            group_id=group_id,
            topic_id=topic_id,
            group_title=group_title,
            creator_id=creator_id,
            creator_name=creator_name,
            performer_id=performer_id,
            performer_name=performer_name,
            priority=priority,
            status=TaskStatus.CREATED,
            task_type=task_type,
            created_at=created_at,
            file_id=file_id
        )

        self.task_cache[task_id] = task
        self.indexes.register_task(task)
        # Добавить логику записи в базу данных в базу данных
        await self.task_database.upsert(task)
        return task

    async def remove_task(self, task_id: str):
        task = self.get_task(task_id)
        if not task:
            return
        self.indexes.remove_task(task)
        self.task_cache.pop(task_id, None)

        await self.task_database.delete(task_id)

    ##############
    async def add_schedule(self,
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
        next_run_at: datetime or None = None,
        every_n_days: int or None = None,
        address: str or None = None,
        topic_id: int or None = None,

    ) -> ScheduledTask:
        """
        Создать и добавить задачу в cache
        """
        schedule_id = uuid4().hex[:16]  # генерим уникальный id
        created_at = datetime.datetime.now().replace(
            second=0,
            microsecond=0
        )
        #
        # if (not next_run_at) and every_n_days:
        #     next_run_at = created_at + datetime.timedelta(days=every_n_days)

        schedule_task = ScheduledTask(
            id=schedule_id,
            title=title,
            description=description,
            address=address,
            group_id=group_id,
            topic_id=topic_id,
            group_title=group_title,
            creator_id=creator_id,
            creator_name=creator_name,
            performer_id=performer_id,
            performer_name=performer_name,
            priority=priority,
            task_type=task_type,
            created_at=created_at,
            every_n_days=every_n_days,
            next_run_at=next_run_at
        )
        self.scheduler_task_cache[schedule_id] = schedule_task
        await self.scheduled_task_database.upsert(schedule_task)
        return schedule_task

    async def create_task_from_scheduler(self, schedule: ScheduledTask) -> Task or None:
        """
        Создаёт Task на базе ScheduledTask.

        Если задача с таким parent_id уже существует
        в task_cache — ничего не делает.
        """

        # ==========================================
        # CHECK EXISTS
        # ==========================================

        for existing_task in self.task_cache.values():

            if getattr(existing_task, "parent_id", '') == schedule.id: # если в кеше есть незавершённая задача
                return None

        task_id = uuid4().hex[:16]  # генерим уникальный id
        datetime_now = datetime.datetime.now()

        new_task = Task(
            task_id=task_id,

            title=schedule.title,
            description=schedule.description,

            group_id=schedule.group_id,
            topic_id=schedule.topic_id,
            group_title=schedule.group_title,

            creator_id=schedule.creator_id,
            creator_name=schedule.creator_name,

            performer_id=schedule.performer_id,
            performer_name=schedule.performer_name,

            priority=schedule.priority,
            address=schedule.address,

            task_type=schedule.task_type,
            status=TaskStatus.CREATED,
            created_at=datetime_now,
            parent_id=schedule.id
            )

        # создаём новую задачу в кеше
        await self.upsert_task(new_task)

        # если задача имеет тип Однократно - значит это задача с отложенным запуском. Удаляем schedule из кеша
        if schedule.task_type == TaskType.ONCE.value:
            await self.remove_task_scheduler(schedule.id)
        else:
            # дальше обновить last_run_at
            schedule.next_run_at = schedule.next_run_at + datetime.timedelta(days=schedule.every_n_days)
            await self.scheduled_task_database.upsert(schedule)

        return new_task

    async def remove_task_scheduler(self, task_scheduler_id) -> ScheduledTask or None:
        scheduler_task = self.scheduler_task_cache.pop(task_scheduler_id, None)
        await self.scheduled_task_database.delete(task_scheduler_id)
        return scheduler_task



