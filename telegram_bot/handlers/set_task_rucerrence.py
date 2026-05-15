from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from telegram_bot.states import CreateTaskStates  # FSM
from telegram_bot.services.user_service import UserService
from telegram_bot.services.task_service import TaskService
from telegram_bot.flows.create_task import show_task_confirmation


router = Router()


@router.message(CreateTaskStates.choosing_repeat)
async def set_task_recurrence_handler(message: Message, state):
    every_n_days = message.text
    if every_n_days.isdigit():
        await state.update_data(every_n_days=int(every_n_days))
        await show_task_confirmation(message, state)
    else:
        await message.answer(text="Ошибка. Необходимо отправить целое число")
        await message.answer(text="👇🏻 Укажите интервал дней для пересоздания задачи. \n<i>Например если ввести “5”, задача будет пересоздаваться раз в 5 дней </i>", parse_mode="HTML")
        await state.set_state(CreateTaskStates.choosing_repeat)

