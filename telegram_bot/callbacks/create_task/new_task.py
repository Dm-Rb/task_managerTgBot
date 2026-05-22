from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from telegram_bot.services.user_service import UserService
from telegram_bot.services.task_service import TaskService

from telegram_bot.services.task_runtime_service import TaskRuntimeService
from telegram_bot.messages.task import get_task_message_by_task_obj
from telegram_bot.models.task import TaskType


router = Router()


@router.callback_query(F.data.startswith("new_task:create"))
async def create_new_task_handker(callback: CallbackQuery, state: FSMContext,
                                  runtime_service: TaskRuntimeService, task_service: TaskService):

    state_data = await state.get_data()
    if state_data.get('scheduler', None):
        return
    # передаём данные в кеш task_service
    task = task_service.add_task(
        title=state_data['template_title'],
        description=state_data['template_description'],
        group_id=state_data['group_id'],
        topic_id=state_data['topic_id'],
        group_title=state_data['group_title'],
        creator_id=callback.from_user.id,
        creator_name=callback.from_user.full_name,
        performer_id=state_data['performer_id'],
        performer_name=state_data['performer_name'],
        priority=state_data['priority'],
        task_type=state_data['task_type'],
        address=state_data.get('address', None)
            )
    await runtime_service.register_new_task(task) # передаём объект в runtime_service для рассылки уведомлений
    # prew_text = "🆕 <b>Вы создали новую задачу</b>\n\n"
    # await callback.message.edit_text(
    #     text=prew_text + get_task_message_by_task_obj(task),
    #     reply_markup=None,
    #     parse_mode="HTML"
    # )
    await callback.message.delete()
    await callback.answer("✅ Задача создана")
    await state.clear()





@router.callback_query(F.data.startswith("new_task:cancel"))
async def performer_select_handler(callback: CallbackQuery, state: FSMContext, task_service: UserService):
    await state.clear()
    await callback.message.delete()
    await callback.answer("❌ Создание новой задачи отменено")

