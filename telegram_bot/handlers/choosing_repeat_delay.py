from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from telegram_bot.states import CreateTaskStates, CreateСashColletionStates
from telegram_bot.flows.create_task import (
    show_schedule_task_confirmation, show_recurrence_task_repeat, show_delay_hours_selection
)
from telegram_bot.messages.cash_collection import cash_collection_creation_message_by_state_data
from telegram_bot.keyboards.cash_collection import confirm_create_new_cash_collection

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
async def choosing_task_delay_handler(message: Message, state: FSMContext):
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
    
@router.message(CreateСashColletionStates.choosing_repeat, F.text)
async def choosing_cash_colletion_repeat_handler(message: Message, state: FSMContext):
    """Хендлер отлавливает состояние choosing_repeat. Ожидает от пользователя ввода числа, которое будет являться
       количеством дней для повторного пересоздания задачи для инкассации
    """
    if message.text.startswith('/'):
        await state.clear()
        await message.answer('Отменено')
        return
    value = message.text
    if value.isdigit():
        await state.update_data(every_n_days=int(value))
        text = await cash_collection_creation_message_by_state_data(state)  # формируем текст сообщения из state.get_data()
        await message.answer(
            text=text,
            reply_markup=confirm_create_new_cash_collection("shedule_сash_collection"),  # префикс для коллбеков
            parse_mode="HTML"
        )        
        await state.set_state(None)
        return
    else:
        await message.answer('Отправьте боту целое число!')
        return
