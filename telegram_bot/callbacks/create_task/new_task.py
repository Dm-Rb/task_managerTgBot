from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from telegram_bot.services.user_service import UserService
from telegram_bot.services.task_runtime_service import TaskRuntimeService
from telegram_bot.messages.task import get_task_message_by_task_obj
from telegram_bot.models.task import TaskType


router = Router(name="create_new_task")


@router.callback_query(F.data.startswith("new_task:create"))
async def create_new_task_handker(callback: CallbackQuery, state: FSMContext, runtime_service: TaskRuntimeService):
    state_data = await state.get_data()
    # передаём данные в кеш task_service
    task = await runtime_service.register_new_task(
        title=state_data['template_title'],
        description=state_data['template_description'],
        group_id=state_data['group_id'],
        group_title=state_data['group_title'],
        creator_id=callback.from_user.id,
        creator_name=callback.from_user.full_name,
        performer_id=state_data['performer_id'],
        performer_name=state_data['performer_name'],
        priority=state_data['priority'],
        task_type=state_data['task_type'],
        every_n_days=state_data.get('every_n_days', None),
        address=state_data.get('address', None)
            )

    prew_text = "🆕 <b>Вы создали новую задачу</b>\n\n"
    await callback.message.edit_text(
        text=prew_text + get_task_message_by_task_obj(task),
        reply_markup=None,
        parse_mode="HTML"
    )
    await callback.answer("✅ Задача создана")
    await state.clear()

    if task.task_type == TaskType.RECURRING:
        pass
        # Тут необходимо добавить логику создания объекта шаблона задачи по расписанию



@router.callback_query(F.data.startswith("new_task:cancel"))
async def performer_select_handler(callback: CallbackQuery, state: FSMContext, task_service: UserService):
    await state.clear()
    await callback.message.delete()
    await callback.answer("❌ Создание новой задачи отменено")

