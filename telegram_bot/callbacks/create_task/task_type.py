from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from telegram_bot.flows.create_task import show_task_confirmation


from telegram_bot.models.task import TaskType
from telegram_bot.states import CreateTaskStates


router = Router(name="task_type")


@router.callback_query(F.data.startswith("task_type:once"))
async def task_type_select_once_handler(callback: CallbackQuery, state: FSMContext):


    await state.update_data(task_type=TaskType.ONCE.value)
    await show_task_confirmation(callback, state)

    return await callback.answer()



    # -----------------------------------------
    # ЦИКЛИЧЕСКАЯ
    # -----------------------------------------

