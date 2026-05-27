from aiogram.types import CallbackQuery
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from telegram_bot.states import CompleteTaskStates  # FSM


async def show_message_attach_photo(message_or_callback: CallbackQuery or Message, state: FSMContext, message_text):
    """Показывает список шаблонов задач"""
    text = message_text + "\n\n" + "📸 Прикрепите фото или видео отчёт о проделанной работе\n👇🏻 👇🏻 👇🏻🔻🔻🔻🔻🔻👇🏻👇🏻👇🏻"
    await message_or_callback.message.answer(text, parse_mode="HTML")

    await state.set_state(CompleteTaskStates.waiting_media)