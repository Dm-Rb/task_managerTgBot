from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from telegram_bot.flows import create_task as flows


router = Router()


@router.callback_query(F.data == "file:next")
async def create_task_template(callback: CallbackQuery, state: FSMContext):
    await flows.show_task_confirmation(callback, state)


@router.callback_query(F.data == "file:_next_")
async def create_task_template(callback: CallbackQuery, state: FSMContext):
    await flows.show_task_confirmation(callback, state)