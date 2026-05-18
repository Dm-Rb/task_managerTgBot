from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from telegram_bot.flows.create_task import show_selected, show_priority_selection, show_task_type_selection
from telegram_bot.models.task import TaskPriority


router = Router()


@router.callback_query(F.data.startswith("priority:select:"))
async def priority_select_handler(callback: CallbackQuery, state: FSMContext):
    """Выбор приоритета задачи"""
    try:
        index = int(callback.data.split(":")[2])
        priority: str = TaskPriority.get_by_index(index)
    except Exception:
        await callback.answer("Ошибка выбора приоритета", show_alert=True)
        return

    # Сохраняем в FSM
    await state.update_data(priority=priority)

    await show_selected(callback, state, 'priority')  # делегируем отображение в flow
    await callback.answer()


@router.callback_query(F.data == "priority:continue")
async def priority_continue_handler(callback: CallbackQuery, state: FSMContext, ):
    """Переход на этап выбора типа задачи"""

    await show_task_type_selection(callback, state)
    await callback.answer()


@router.callback_query(F.data == "priority:back")
async def priority_back_handler(callback: CallbackQuery, state: FSMContext):
    """Возврат к выбору приоритета"""
    await show_priority_selection(callback, state)
    await callback.answer()