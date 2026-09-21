from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from telegram_bot.states import CreateTaskStates
from telegram_bot.flows.create_task import show_address_selection
from telegram_bot.services.template_service import TemplateService
from telegram_bot.states import CreateСashColletionStates


router = Router()



@router.callback_query(F.data == "сash_collection_reccurence:back")
async def сash_collection_reccurence_back(callback: CallbackQuery, state: FSMContext):
    # удаляем сообщение целиком
    await callback.message.delete()
    # переводим FSM
    
    # отправляем новое сообщение
    await callback.message.answer(
        "Введите интервал (чмсло дней) через который задача будет пересоздаваться автоматически 👇🏻"
    )
    await state.set_state(CreateСashColletionStates.choosing_repeat)

@router.callback_query(F.data == "сash_collection_reccurence:continue")
async def ash_collection_reccurence_continue(callback: CallbackQuery, state: FSMContext):
    """Перейти на этап ввода интервала дней"""
    # удаляем сообщение целиком
    await callback.message.edit_text()
    await state.set_state(None)