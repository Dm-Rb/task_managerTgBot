from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from telegram_bot.services.cash_collection_service import CashCollectionService
from telegram_bot.services.task_service import TaskService
from telegram_bot.services.task_runtime_service import TaskRuntimeService
import datetime
from telegram_bot.messages.task import get_schedule_task_creation_message_by_state_schedule_task_obj as create_message
from telegram_bot.models.task import TaskType


router = Router()


@router.callback_query(F.data.startswith("sheduled_cash_collection:create"))
async def create_new_scheduler_task_handler(callback: CallbackQuery, 
                                            state: FSMContext,
                                            cash_collection_service: CashCollectionService):
    state_data = await state.get_data()
    if not state_data.get('scheduler', None): # если нет ключа scheduler - завершить
        return
    # передаём данные в кеш task_service
    sheduled_task = await cash_collection_service.create_sheduler(
            city_id=state_data.get("city_id"),
            city=state_data.get("city"),
            description=state_data.get("description"),
            creator_id=state_data.get("creator_id"),
            creator_name=state_data.get("creator_name"),
            performer_id=state_data.get("performer_id"),
            performer_name=state_data.get("performer_name"),
            every_n_days=state_data.get("every_n_days"),
        )
    print(sheduled_task.id)
    print(sheduled_task.next_run_at)
