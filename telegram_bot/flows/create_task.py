from aiogram.types import CallbackQuery
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from telegram_bot.keyboards import create_task as keyboards
from telegram_bot.states import CreateTaskStates  # FSM
from telegram_bot.messages.task import get_task_creation_message_by_state_data
from telegram_bot.services.user_service import UserService
from telegram_bot.services.group_service import GroupService

from telegram_bot.services.task_service import TaskService


async def show_templates_selection(message_or_callback, state: FSMContext, task_service: TaskService, additional_text=""):
    """Показывает список шаблонов (используется и при старте, и после создания)"""
    # message_or_callback < сюда может прийти или message, или callback
    task_templates = task_service.get_all_templates()

    text = f"{additional_text}📔 <b>Выберите шаблон задачи или создайте новый</b>"

    keyboard = keyboards.task_templates_keyboard(task_templates=task_templates)

    if isinstance(message_or_callback, Message):  # отправили  /create_task
        await message_or_callback.answer(
            text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    else:  # нажатие на инлайн кнопку
        await message_or_callback.message.edit_text(
            text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )

    await state.set_state(CreateTaskStates.choosing_template)


async def show_groups_selection(message_or_callback, state: FSMContext, group_service: GroupService):
    """Показывает список групп"""
    groups = group_service.get_all_groups()
    if not groups:
        await state.clear()
        text = "Бот не состоит ни в одной группе. Добавьте бота в группу"
        await message_or_callback.message.edit_text(text, reply_markup=None, parse_mode="HTML")
        return

    keyboard = keyboards.groups_keyboard(groups=groups, page=0)
    text = "<b>👥 Выберите группу для задачи:</b>"
    await message_or_callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await state.set_state(CreateTaskStates.choosing_group)


async def show_performer_selection(callback: CallbackQuery, state: FSMContext, performers: list):
    """Показываем выбор исполнителя"""

    await callback.message.edit_text(
        text=f"👨🏼‍💼 <b>Выберите исполнителя:</b>",
        reply_markup=keyboards.performers_keyboard(performers),
        parse_mode="HTML"
    )

    await state.set_state(CreateTaskStates.choosing_performer)


async def show_no_performers_in_group(callback: CallbackQuery, state: FSMContext,
                                      group_service: GroupService, group_id: int):
    """Показываем сообщение, если в группе нет сотрудников и возвращаемся к выбору из списка групп"""
    group_title = group_service.get_group_by_id(group_id).title
    groups = group_service.get_all_groups()

    keyboard = keyboards.groups_keyboard(groups=groups, page=0)
    text = f'В группе "<b>{group_title}</b>" нет ни одного участника с ролью "Сотрудник".\n\n' \
           f'Пожалуйста, выберите другую группу:'

    await callback.message.edit_text(
        text=text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await state.set_state(CreateTaskStates.choosing_group)


async def show_priority_selection(callback: CallbackQuery, state: FSMContext):
    """Показываем выбора приоритета"""
    text = "<b>🚀 Выберите приоритет задачи:</b>"

    await callback.message.edit_text(
        text=text,
        reply_markup=keyboards.priority_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(CreateTaskStates.choosing_priority)


async def show_task_type_selection(callback: CallbackQuery, state: FSMContext):
    """Показать выбор типа задачи (однократная / циклическая)"""
    text = "<b>🕘 Выберите тип задачи:</b>"

    await callback.message.edit_text(
        text=text,
        reply_markup=keyboards.task_type_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(CreateTaskStates.choosing_task_type)

async def show_task_confirmation(
    callback: CallbackQuery,
    state: FSMContext
):
    """Показывает финальное подтверждение создания задачи"""

    text = await get_task_creation_message_by_state_data(state)

    await callback.message.edit_text(
        text=text,
        reply_markup=keyboards.confirm_create_new_task(),
        parse_mode="HTML"
    )

    await state.set_state(CreateTaskStates.waiting_confirmation)

async def show_selected(callback: CallbackQuery, state: FSMContext, callback_data_prefix: str):
    """Показывает сообщение с выбранной информацией + клавиатуру Продолжить/Назад"""
    text = await get_task_creation_message_by_state_data(state)  # формируем текст сообщения из state.get_data()

    await callback.message.edit_text(
        text=text,
        reply_markup=keyboards.confirm_or_back_keyboard(callback_data_prefix),  # префикс для коллбеков
        parse_mode="HTML"
    )
