from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from telegram_bot.models.task import TaskType
from telegram_bot.flows.create_task import (show_selected, show_task_type_selection, show_schedule_task_confirmation,
                                            show_task_recurring_selection, show_recurrence_task_repeat,
                                            show_delay_hours_selection, upload_files)


router = Router()


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


@router.callback_query(F.data.startswith("recurrence_task:repeat:"))
async def recurrence_task_repeat_handler(callback: CallbackQuery, state: FSMContext):
    try:
        every_n = callback.data.split(":")[2] # '1' or 'set'
    except:
        await callback.answer("Ошибка при выборе исполнителя", show_alert=True)
        return
    if every_n == 'set':
        # меняем состояние, удаляем сообщение. срабатывает хендлер на сосотояние который просит пользователя ввести данные
        await show_recurrence_task_repeat(callback, state)
    elif every_n == "1":
        await state.update_data(every_n_days=1)
        await upload_files(callback, state)


@router.callback_query(F.data.startswith("task_type:once"))
async def task_type_select_once_handler(callback: CallbackQuery, state: FSMContext):
    await state.update_data(task_type=TaskType.ONCE.value)
    await show_delay_hours_selection(callback, state)
    await callback.answer()

