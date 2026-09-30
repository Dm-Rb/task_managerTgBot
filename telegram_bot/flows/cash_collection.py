from aiogram.types import CallbackQuery
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from telegram_bot.keyboards import cash_collection as keyboards
from telegram_bot.keyboards.cash_collection import performers_keyboard 

from telegram_bot.states import CreateTaskStates  # FSM
from telegram_bot.messages.task import get_task_creation_message_by_state_data, \
    get_schedule_task_creation_message_by_state_data
from telegram_bot.services.user_service import UserService
from telegram_bot.services.group_service import GroupService
from aiogram.utils.keyboard import InlineKeyboardBuilder
from telegram_bot.services.task_service import TaskService
from telegram_bot.services.template_service import TemplateService

from telegram_bot.storage.task_cache import AddressTemplate


async def show_cities_selection(message_or_callback: CallbackQuery or Message, state: FSMContext,
                                   template_service: TemplateService, callback_prefix: str, additional_text=""):
    """Показывает список доступных городов"""


    text = f"{additional_text}🏢 <b>Выберите город</b>"
    keyboard = keyboards.cities_keyboard(template_service.cities, callback_prefix)

    if isinstance(message_or_callback, Message): 
        if not template_service.cities:
            await state.clear()
            text = "Не доступно ни одного города. Создайте новые записи через панель управления в браузере"
            keyboard = None
        await message_or_callback.answer(
            text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    else:  # нажатие на инлайн кнопку
        if not template_service.cities:
            await state.clear()
            return await message_or_callback.answer("Не доступно ни одного города. Создайте новые записи через панель управления в браузере", show_alert=True)
            
        await message_or_callback.message.edit_text(
            text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
async def show_performer_selection(callback: CallbackQuery, state: FSMContext, performers: list):
    """Показываем выбор исполнителя"""
    if performers_keyboard(performers):
        await callback.message.edit_text(
            text=f"👨🏼‍💼 <b>Выберите исполнителя:</b>",
            reply_markup=performers_keyboard(performers),
            parse_mode="HTML"
        )
    else:
        await callback.message.edit_text(
        text=f"<b>Нет ни одного исполнителя в списке пользователей бота\n/menu</b>",
        reply_markup=None,
        parse_mode="HTML"
    )
        await state.clear()

