
import asyncio
from datetime import datetime
from telegram_bot.services.task_runtime_service import TaskRuntimeService
from telegram_bot.services.task_service import TaskService
from telegram_bot.models.task import TaskType


class SchedulerService:

    def __init__(self, task_service: TaskService, runtime_service: TaskRuntimeService):
        self.task_service = task_service
        self.runtime_service = runtime_service
        self.is_running = False

    async def start(self):

        self.is_running = True

        while self.is_running:
            try:
                await self.tick()
            except Exception as e:
                print(f"[SCHEDULER ERROR] {e}")
            # проверка раз в минуту
            await asyncio.sleep(60)

    async def tick(self):

        now = datetime.now().replace(second=0, microsecond=0)

        for schedule_key in self.task_service.scheduler_task_cache.keys():

            # SKIP INVALID
            schedule_task = self.task_service.scheduler_task_cache[schedule_key]
            # if not schedule.next_run_at:
            #     continue

            if now >= schedule_task.next_run_at:
                # создаём задачу
                task = await self.task_service.create_task_from_scheduler(
                    schedule=schedule_task
                )

                if task:
                    await self.runtime_service.register_new_task(task)
