
import asyncio
from datetime import datetime
from telegram_bot.services.task_runtime_service import TaskRuntimeService
from telegram_bot.services.cash_collection_runtime_service import CashCollectionRuntimeService
from telegram_bot.services.task_service import TaskService
from telegram_bot.services.cash_collection_service import CashCollectionService
import traceback


class SchedulerService:

    def __init__(self, 
                 task_service: TaskService, 
                 cash_collection_service: CashCollectionService,
                 task_runtime_service: TaskRuntimeService,
                 cash_collection_runtime_service: CashCollectionRuntimeService):
        self.task_service = task_service
        self.cash_collection_service = cash_collection_service
        self.task_runtime_service = task_runtime_service
        self.cash_collection_runtime_service = cash_collection_runtime_service
        
        self.is_running = False

    async def start(self):

        self.is_running = True

        while self.is_running:
            await self.tick()

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
                    await self.task_runtime_service.register_new_task(task)
              
        for cc_schedule_key in self.cash_collection_service.sheduled_tasks.keys():

            cash_collection_schedule_task = self.cash_collection_service.sheduled_tasks[cc_schedule_key]                     
            if now >= cash_collection_schedule_task.next_run_at:
                # создаём задачу
                try:
                    cash_collection_task = await self.cash_collection_service.create_task(cash_collection_schedule_task)
                    if cash_collection_task:
                        await self.cash_collection_runtime_service.register_new_task(cash_collection_task)
                except Exception:
                    traceback.print_exc()
                    raise

