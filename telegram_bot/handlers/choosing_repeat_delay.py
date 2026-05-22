from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from telegram_bot.states import CreateTaskStates
from telegram_bot.flows.create_task import (
    show_schedule_task_confirmation, show_recurrence_task_repeat, show_delay_hours_selection
)


router = Router()


@router.message(CreateTaskStates.choosing_repeat, F.text)
async def choosing_task_repeat_handler(message: Message, state: FSMContext):
    """Хендлер отлавливает состояние choosing_repeat. Ожидает от пользователя ввода числа, которое будет являться
       количеством дней для повторного пересоздания задачи
    """
    value = message.text
    if value.isdigit():
        await state.update_data(every_n_days=int(value))
        await state.set_state(CreateTaskStates.waiting_confirmation)
        await show_schedule_task_confirmation(message, state)
        return
    else:
        await message.answer('Отправьте боту целое число!')
        await state.set_state(CreateTaskStates.choosing_repeat)
        await show_recurrence_task_repeat(message, state)
        return


@router.message(CreateTaskStates.choosing_delay, F.text)
async def choosing_task_repeat_handler(message: Message, state: FSMContext):
    """Хендлер отлавливает состояние choosing_repeat. Одидает от пользователя ввода числа, которое будет являться
       количеством дней для повторного пересоздания задачи
    """
    value = message.text
    if value.isdigit():
        await state.update_data(delay_hours=int(value))
        await state.set_state(CreateTaskStates.waiting_confirmation)
        await show_schedule_task_confirmation(message, state)

        return
    else:
        await message.answer('Отправьте боту целое число!')
        await show_delay_hours_selection(message, state)
        await state.set_state(CreateTaskStates.choosing_delay)

        return
