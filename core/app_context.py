# Cоздаёт все зависимости
from telegram_bot.storage.user_cache import UserCache
from telegram_bot.storage.group_cache import GroupCache
from telegram_bot.storage.task_cache import TaskCache

from telegram_bot.services.template_service import TemplateService
from telegram_bot.services.user_service import UserService
from telegram_bot.services.group_service import GroupService
from telegram_bot.services.task_service import TaskService
from telegram_bot.services.notification_service import NotificationService
from telegram_bot.services.task_runtime_service import TaskRuntimeService
from telegram_bot.services.scheduler_service import SchedulerService

from database.repositories.user import UserRepository
from database.repositories.group import GroupRepository
from database.repositories.task import TaskRepository
from database.repositories.scheduled_task import ScheduledTaskRepository

from database.repositories.task_tittle import TaskTittleRepository
from database.repositories.city import CityRepository
from database.repositories.adress import AdressRepository



class AppContext:

    def __init__(self, bot):
        

        # repositories
        self.user_database = UserRepository()
        self.group_database = GroupRepository()
        self.task_database = TaskRepository()
        self.scheduled_task_database = ScheduledTaskRepository()        
        self.task_tittle_database = TaskTittleRepository()
        self.city_database = CityRepository()
        self.adress_database = AdressRepository()

        # caches
        self.user_cache = UserCache()
        self.group_cache = GroupCache()
        self.task_cache = TaskCache()

        # services
        self.template_service = TemplateService(
            self.task_tittle_database,
            self.city_database,
            self.adress_database
        )

        self.user_service = UserService(
            self.user_cache,
            self.user_database
        )

        self.group_service = GroupService(
            self.group_cache,
            self.group_database
        )

        self.task_service = TaskService(
            self.task_cache,
            self.task_database,
            self.scheduled_task_database
        )

        self.notification_service = NotificationService(bot)

        self.runtime_service = TaskRuntimeService(
            self.task_service,
            self.notification_service,
            self.user_service
        )

        self.scheduler_service = SchedulerService(
            task_service=self.task_service,
            runtime_service=self.runtime_service
        )

    async def warm_up(self):
        await self.user_service.warm_up()
        await self.group_service.warm_up()
        await self.task_service.warmup()
        await self.template_service.warmup()