from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from telegram_bot.keyboards.logout import logout_keyboard


router = Router()


class LogoutStates(StatesGroup):
    waiting_confirm = State()


@router.message(Command("logout"))
async def logout_start(message: Message, user_service, state: FSMContext):
    user = user_service.get_user_by_id(message.from_user.id)
    if not user:
        return
    if not user.role in (1, 2): # если роль 0 - не реагировать на команду
        return

    await state.set_state(LogoutStates.waiting_confirm)

    await message.answer(
        "Вы действительно хотите разлогиниться?",
        reply_markup=await logout_keyboard()
    )


@router.message(LogoutStates.waiting_confirm, F.text == "Да")
async def logout_confirm(message: Message, state: FSMContext, user_service):

    await user_service.logout(message.from_user.id)

    await state.clear()

    await message.answer(
        "Вы успешно разлогинились",
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(LogoutStates.waiting_confirm, F.text == "Нет")
async def logout_cancel(message: Message, state: FSMContext):

    await state.clear()

    await message.answer(
        "Вы отменили выход",
        reply_markup=ReplyKeyboardRemove()
    )