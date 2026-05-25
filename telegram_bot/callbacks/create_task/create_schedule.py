from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from telegram_bot.services.user_service import UserService
from telegram_bot.services.task_service import TaskService
from telegram_bot.services.task_runtime_service import TaskRuntimeService
import datetime
from telegram_bot.messages.task import get_schedule_task_creation_message_by_state_schedule_task_obj as create_message
from telegram_bot.models.task import TaskType


router = Router()


@router.callback_query(F.data.startswith("create_schedule:create"))
async def create_new_scheduler_task_handler(callback: CallbackQuery, state: FSMContext,
                                            runtime_service: TaskRuntimeService, task_service: TaskService):
    state_data = await state.get_data()
    if not state_data.get('scheduler', None): # если нет ключа scheduler - завершить
        return
    # передаём данные в кеш task_service
    if state_data.get('delay_hours', None):  # одноразовая задача с отложенным запуском
        created_at = datetime.datetime.now().replace(second=0, microsecond=0)
        next_run_at = created_at + datetime.timedelta(hours=state_data['delay_hours'])
    else:
        next_run_at = datetime.datetime.now().replace(second=0, microsecond=0) # задача по расписанию новая создаётся сразу

    schedule_task = await task_service.add_schedule(
        title=state_data.get('template_title', None),
        description=state_data.get('template_description', None),
        group_id=state_data.get('group_id', None),
        group_title=state_data.get('group_title', None),
        creator_id=callback.from_user.id,
        creator_name=callback.from_user.full_name,
        performer_id=state_data.get('performer_id', None),
        performer_name=state_data.get('performer_name', None),
        priority=state_data.get('priority', None),
        task_type=state_data.get('task_type', None),
        address=state_data.get('address', None),
        topic_id=state_data.get('topic_id', None),
        every_n_days=state_data.get('every_n_days', None),
        next_run_at=next_run_at
    )
    prew_text = "🆕 <b>Вы создали новую конфигурацию задачи по расписанию</b>\n\n"
    await callback.message.edit_text(
        text=prew_text + create_message(schedule_task),
        reply_markup=None,
        parse_mode="HTML"
    )
    await callback.answer("✅ Шаблон задачи создан")
    await state.clear()


@router.callback_query(F.data.startswith("create_schedule:cancel"))
async def performer_select_handler(callback: CallbackQuery, state: FSMContext, task_service: UserService):
    await state.clear()
    await callback.message.delete()
    await callback.answer("❌ Создание нового шаблона задачи отменено")

