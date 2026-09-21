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
                                   template_service: TemplateService, additional_text=""):
    """Показывает список шаблонов задач"""
    task_tittles = await template_service.get_all_task_tittles()

    text = f"{additional_text}🏢 <b>Выберите город для задач инкассации</b>"
    if not template_service.cities:
        text += "\n Не доступно ни одного города."
        await message_or_callback.answer(
                    text,
                    parse_mode="HTML"
                )
        await state.clear()
        return
    keyboard = keyboards.cities_keyboard(template_service.cities)

    if isinstance(message_or_callback, Message): 
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
        
async def show_performer_selection(callback: CallbackQuery, performers: list):
    """Показываем выбор исполнителя"""

    await callback.message.edit_text(
        text=f"👨🏼‍💼 <b>Выберите исполнителя:</b>",
        reply_markup=performers_keyboard(performers),
        parse_mode="HTML"
    )

