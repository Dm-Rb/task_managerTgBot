from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from telegram_bot.states import CreateTaskStates  # FSM
from telegram_bot.services.user_service import UserService
from telegram_bot.services.task_service import TaskService
from telegram_bot.flows.create_task import show_address_selection


router = Router()


@router.message(CreateTaskStates.waiting_address_template)
async def save_address_template(message: Message, state: FSMContext, task_service: TaskService):
    address = message.text.strip()
    if len(address) >= 47:
        address = address[:47]  # что бы влезло в callback_data

    task_service.add_address_template(address)
    # Делегируем отображение в flow
    await show_address_selection(message, state, task_service, "💬 Новый шаблон создан\n\n")
