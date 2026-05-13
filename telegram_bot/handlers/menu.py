from aiogram import Router, F
from aiogram.filters import Command

from telegram_bot.keyboards.menu import main_menu_keyboard
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from telegram_bot.states import CreateTaskStates  # FSM

from telegram_bot.flows.create_task import show_templates_selection
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from telegram_bot.keyboards.logout import logout_keyboard



router = Router()


@router.message(Command("menu"))
async def show_tasks_handler(message: Message, user_service):
    user = user_service.cache.get(message.from_user.id)
    if not user:
        return
    if not user.role in (1, 2): # если роль 0 - не реагировать на команду
        return await message.answer(text='Для отображения меню необходима авторизация')

    user = user_service.cache.get(message.from_user.id)
    await message.answer(text='Выберите пункт меню из списка:', reply_markup=main_menu_keyboard(user.role))

@router.message(F.text == "📋 Мои задачи")
async def show_tasks_button(message: Message, runtime_service, user_service):
    user = user_service.cache.get(message.from_user.id)
    if user.role == 1:  # исполнитель задачи
        text = "📝 <b>Список ваших активных задач:</b>"
        await message.answer(text=text, parse_mode='HTML')
        await runtime_service.send_tasks_to_performer(message.from_user.id)
    elif user.role == 2:  # создатель задачи
        text = "📝 <b>Список созданных вами задач:</b>"
        await message.answer(text=text, parse_mode='HTML')
        await runtime_service.send_tasks_to_creator(message.from_user.id)
    else:
        return

@router.message(F.text == "➕ Создать новую задачу")
async def show_tasks_button(message: Message, state: FSMContext, task_service ,
                                user_service):

    """ Старт создания задачи """
    user = user_service.cache.get(message.from_user.id)
    if not user:
        return
    if not user.role in (1, 2): # если роль 0 - не реагировать на команду
        return
    # очищаем состояние
    await state.clear()
    is_user_admin = await user_service.is_user_admin(message.from_user.id)
    if not is_user_admin:
        return await message.answer('У вас не достаточно прав для создания задач')

    # Делегируем отображение в flow
    await show_templates_selection(message, state, task_service)
    await state.set_state(CreateTaskStates.choosing_template)

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