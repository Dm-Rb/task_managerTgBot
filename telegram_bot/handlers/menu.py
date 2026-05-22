

from telegram_bot.keyboards.menu import main_menu_keyboard

from telegram_bot.states import CreateTaskStates  # FSM

from telegram_bot.flows.create_task import show_templates_selection
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from telegram_bot.keyboards.logout import logout_keyboard


router = Router()


@router.message(Command("menu"))
async def show_tasks_handler(message: Message, user_service, state: FSMContext):
    user = user_service.cache.get(message.from_user.id)
    if not user:
        return
    if not user.role in (1, 2): # если роль 0 - не реагировать на команду
        return await message.answer(text='Для отображения меню необходима авторизация: /start')

    user = user_service.cache.get(message.from_user.id)
    await message.answer(text='Выберите пункт меню из списка:', reply_markup=main_menu_keyboard(user.role))

    await state.clear()

@router.message(F.text == "➕ Создать новую задачу")
async def create_new_task_handler(message: Message, state: FSMContext, task_service, user_service):
    """ Старт создания задачи """
    user = user_service.cache.get(message.from_user.id)
    if not user:
        return
    if not user.role in (1, 2): # если роль 0 - не реагировать на команду
        return
    # очищаем состояние
    await state.clear()
    is_user_admin = user_service.is_user_admin(message.from_user.id)
    if not is_user_admin:
        return await message.answer('У вас не достаточно прав для создания задач')

    # Делегируем отображение в flow
    await show_templates_selection(message, state, task_service)
    await state.set_state(CreateTaskStates.choosing_template)


@router.message(F.text == "📅 Создать конфигурацию задачи по расписанию")
async def create_new_scheduler_task_handler(message: Message, state: FSMContext, task_service, user_service):
    """ Старт создания задачи по расписанию"""
    user = user_service.cache.get(message.from_user.id)
    if not user:
        return
    if user.role in (0, 1):  # если не роль 2 - не реагировать на команду
        return
    # очищаем состояние
    await state.clear()
    is_user_admin = user_service.is_user_admin(message.from_user.id)
    if not is_user_admin:
        return await message.answer('У вас не достаточно прав для создания задач')

    await show_templates_selection(message, state, task_service, scheduler=True)
    await state.set_state(CreateTaskStates.choosing_template)


@router.message(F.text == "📋 Мои задачи")
async def show_tasks_button(message: Message, runtime_service, user_service):
    text = "📝 <b>Список ваших активных задач:</b>"
    await message.answer(text=text, parse_mode='HTML')
    await runtime_service.send_tasks_to_performer(message.from_user.id)

@router.message(F.text == "🗓 Список всех активных задач")
async def show_all_tasks_button(message: Message, runtime_service, user_service):
    user = user_service.cache.get(message.from_user.id)
    if user.role != 2:
        return
    text = "📝 Список всех активных задач:"
    await message.answer(text=text, parse_mode='HTML')
    await runtime_service.get_all_tasks(message.from_user.id)
    # if user.role == 1:  # исполнитель задачи


@router.message(F.text == "📆 Список всех конфигураций задач по-расписанию")
async def show_all_tasks_button(message: Message, runtime_service, user_service):
    user = user_service.cache.get(message.from_user.id)
    if user.role != 2:
        return
    text = "📆 Список всех конфигураций задач по-расписанию:"
    await message.answer(text=text, parse_mode='HTML')
    await runtime_service.get_all_scheduler_tasks(message.from_user.id)


class LogoutStates(StatesGroup):
    waiting_confirm = State()

@router.message(F.text == "🚪 Разлогиниться")
@router.message(Command("logout"))
async def logout_start(message: Message, user_service, state: FSMContext):
    user = user_service.cache.get(message.from_user.id)
    if not user:
        return
    if not user.role in (1, 2): # если роль 0 - не реагировать на команду
        return

    await state.set_state(LogoutStates.waiting_confirm)

    await message.answer(
        "Вы действительно хотите разлогиниться?",
        reply_markup=await logout_keyboard()
    )
