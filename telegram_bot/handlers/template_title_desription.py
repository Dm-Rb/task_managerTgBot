from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from telegram_bot.states import CreateTaskStates  # FSM
from telegram_bot.flows.create_task import show_tittles_selection
from telegram_bot.messages.task import get_task_creation_message_by_state_data
from telegram_bot.keyboards import create_task as keyboards


router = Router(name="handlers_create_task")


@router.message(CreateTaskStates.waiting_template_title)
async def template_title_handler(message: Message, state: FSMContext, template_service):
    if message.text.startswith('/'):
        await state.clear()
        await message.answer('Отменено')
        return

    # записываем в фсм титульник нового шаблона
    await state.update_data(template_title=message.text)
    # добавить в кеш
    await template_service.add_task_tittle(message.text, False)
    # отобразить обновлённую конструкцию
    await show_tittles_selection(message, state, template_service)
    # удалить состояние reateTaskStates.waiting_template_description при  этом сохранив остальные данные
    await state.set_state(None)
    


@router.message(CreateTaskStates.waiting_template_description)
async def template_description_handler(message: Message, state: FSMContext, task_service):
    if message.text.startswith('/'):
        await state.clear()
        await message.answer('Отменено')
        return
    await state.update_data(template_description=message.text)
    # Показывает сообщение с текущим выбором + кнопки назад\подтвердить
    text = await get_task_creation_message_by_state_data(state)  # формируем текст сообщения из state.get_data()
    await message.answer(
        text=text,
        reply_markup=keyboards.confirm_or_back_keyboard("task_description"),  # префикс для коллбеков
        parse_mode="HTML"
    )
    # удалить состояние reateTaskStates.waiting_template_description при  этом сохранив остальные данные
    await state.set_state(None)

