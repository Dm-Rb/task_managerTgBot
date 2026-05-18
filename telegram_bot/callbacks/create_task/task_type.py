from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from telegram_bot.flows.create_task import show_task_confirmation
from telegram_bot.models.task import TaskType
from telegram_bot.flows.create_task import show_selected, show_task_type_selection, show_task_recurring_selection


router = Router()


@router.callback_query(F.data.startswith("task_type:once"))
async def task_type_select_once_handler(callback: CallbackQuery, state: FSMContext):
    await state.update_data(task_type=TaskType.ONCE.value)
    await show_task_confirmation(callback, state)

    return await callback.answer()


@router.callback_query(F.data.startswith("task_type:recurring"))
async def task_type_select_once_handler(callback: CallbackQuery, state: FSMContext):
    await state.update_data(task_type=TaskType.RECURRING.value)

    await show_selected(callback, state, 'recurring')  # делегируем отображение в flow
    await callback.answer()


@router.callback_query(F.data.startswith("recurring:continue"))
async def task_type_select_once_handler(callback: CallbackQuery, state: FSMContext):
    await show_task_recurring_selection(callback, state)
    await callback.answer()


@router.callback_query(F.data.startswith("recurring:back"))
async def task_type_select_once_handler(callback: CallbackQuery, state: FSMContext):
    await show_task_type_selection(callback, state)
    await callback.answer()