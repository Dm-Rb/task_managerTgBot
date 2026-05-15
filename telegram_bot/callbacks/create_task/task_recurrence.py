from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from telegram_bot.flows.create_task import show_task_confirmation
from telegram_bot.models.task import TaskType
from telegram_bot.states import CreateTaskStates


router = Router(name="task_recurrence")

@router.callback_query(F.data.startswith("recurrence_task:repeat:"))
async def performer_select_handler(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора исполнителя (прессбатн)"""
    try:
        every_n = callback.data.split(":")[2] # '1' or 'set'
    except:
        await callback.answer("Ошибка при выборе исполнителя", show_alert=True)
        return


    if every_n == 'set':
        await state.set_state(CreateTaskStates.choosing_repeat)
        # меняем состояние, удаляем сообщение. срабатывает хендлер на сосотояние который просит пользователя ввести данные
        text = "👇🏻 Укажите интервал дней для пересоздания задачи. \n<i>Например если ввести “5”, задача будет пересоздаваться раз в 5 дней </i>"
        return await callback.message.edit_text(
            text,
            reply_markup=None,
            parse_mode="HTML"
        )
    elif every_n == "1":
        await state.update_data(every_n_days=1)
        await state.set_state(CreateTaskStates.waiting_confirmation)
        await show_task_confirmation(callback, state)
