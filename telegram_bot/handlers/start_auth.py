from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from core.config import settings


router = Router()
ROLES = {2: "Администратор", 1: "Сотрудник"}


class AuthStates(StatesGroup):
    waiting_for_password = State()


@router.message(Command("start"))
async def cmd_start(message: Message, user_service, state: FSMContext):

    user = await user_service.register_in_cache(message.from_user)

    if user.is_banned:
        await message.answer("Вы заблокированы")
        return

    if user.role in (1, 2):
        await message.answer(f"Вы уже авторизованы как {ROLES[user.role]}")
        return
    await state.set_state(AuthStates.waiting_for_password)
    await state.update_data(attempts=user.failed_attempts)
    await message.answer("Введите пароль")


@router.message(AuthStates.waiting_for_password)
async def process_password(message: Message, user_service, state: FSMContext):
    user = await user_service.register_in_cache(message.from_user)

    result = await user_service.password(user, message.text)

    if result:
        await state.clear()
        return await message.answer(f"Вы вошли как {ROLES[user.role]}")

    if not user.is_banned:
    # invalid
        await message.answer(
            f"Неверный пароль. Осталось попыток: {settings.MAX_ATTS_PSW - user.failed_attempts}"
        )
    else:
        await state.clear()
        return await message.answer("Неверный пароль. Вы заблокированы")

    await state.update_data(attempts=user.failed_attempts)