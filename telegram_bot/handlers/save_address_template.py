from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from telegram_bot.states import CreateTaskStates  # FSM
from telegram_bot.services.user_service import UserService
from telegram_bot.services.task_service import TaskService
from telegram_bot.flows.create_task import show_templates_selection

router = Router()

@router.message(CreateTaskStates.waiting_address_template)
async def save_address_template(
    message: Message,
    state: FSMContext,
    task_service
):

    address = message.text.strip()

    task_service.add_address_template(address)

    await message.answer(
        "✅ Шаблон адреса сохранён"
    )

    from telegram_bot.flows.create_task import show_address_selection

    fake_callback = type(
        "obj",
        (),
        {"message": message}
    )

    await show_address_selection(
        fake_callback,
        state,
        task_service
    )