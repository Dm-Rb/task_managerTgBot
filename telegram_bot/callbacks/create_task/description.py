from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from telegram_bot.states import CreateTaskStates
from telegram_bot.flows.create_task import show_address_selection
from telegram_bot.services.template_service import TemplateService


router = Router()



@router.callback_query(F.data == "task_description:back")
async def template_back_handler(callback: CallbackQuery, state: FSMContext):
    """Вернуться на этап выбора заголовка"""

    await callback.message.delete()
    # переводим FSM
    await state.set_state(CreateTaskStates.waiting_template_description)
    # отправляем новое сообщение
    await callback.message.answer(
        "Введите описание для задачи 👇🏻"
    )

@router.callback_query(F.data == "task_description:continue")
async def template_continue_handler(callback: CallbackQuery, state: FSMContext, template_service: TemplateService):
    """Перейти на этап выбоа адреса"""
    # отображаем адреса
    await show_address_selection(callback, state, template_service)
