from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from telegram_bot.states import CreateTaskStates  # FSM
from telegram_bot.services.user_service import UserService
from telegram_bot.services.task_service import TaskService
from telegram_bot.flows.create_task import show_templates_selection


router = Router()


@router.message(CreateTaskStates.waiting_template_title)
async def template_title_handler(message: Message, state: FSMContext):

    # записываем в фсм титульник нового шаблона
    await state.update_data(template_title=message.text)
    # меняем состояние
    await state.set_state(CreateTaskStates.waiting_template_description)

    await message.answer("Введите описание задачи 👇🏻")


@router.message(CreateTaskStates.waiting_template_description)
async def template_description_handler(message: Message, state: FSMContext, task_service):

    # достаём из фсм титульник нового шаблона
    data = await state.get_data()
    title = data["template_title"]

    # добавляем новый шаблон в
    description = message.text

    task_service.add_task_template(
        title=title,
        description=description
    )
    # Делегируем отображение в flow
    await show_templates_selection(message, state, task_service, "💬 Новый шаблон \n\n")
    await state.set_state(CreateTaskStates.choosing_template)


