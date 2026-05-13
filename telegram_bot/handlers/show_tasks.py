from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from telegram_bot.states import CreateTaskStates  # FSM
from telegram_bot.services.user_service import UserService
from telegram_bot.services.task_runtime_service import TaskRuntimeService
from telegram_bot.flows.create_task import show_templates_selection


router = Router(name="handlers_show_task")


@router.message(Command("show_tasks"))
async def show_tasks_handler(message: Message, runtime_service, user_service):

    user = user_service.cache.get(message.from_user.id)
    if user.role == 1: # исполнитель задачи
        text = "📝 <b>Список ваших активных задач:</b>"
        await message.answer(text=text, parse_mode='HTML')
        await runtime_service.send_tasks_to_performer(message.from_user.id)
    elif user.role == 2: # создатель задачи
        text = "📝 <b>Список созданных вами задач:</b>"
        await message.answer(text=text, parse_mode='HTML')
        await runtime_service.send_tasks_to_creator(message.from_user.id)
    else:
        return



