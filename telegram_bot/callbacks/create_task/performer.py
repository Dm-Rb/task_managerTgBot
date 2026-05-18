from aiogram import Router, F
from aiogram.types import CallbackQuery
from telegram_bot.keyboards.create_task import performers_keyboard
from aiogram.fsm.context import FSMContext
from telegram_bot.flows import create_task as flows
from telegram_bot.services.user_service import UserService


router = Router()


@router.callback_query(F.data.startswith("performer:page:"))
async def performer_page_handler(callback: CallbackQuery, state: FSMContext, user_service: UserService):
    """Пагинация списка исполнителей. Изменяет клавиатуру"""
    try:
        page = int(callback.data.split(":")[2])
    except:
        await callback.answer("Ошибка", show_alert=True)
        return

    data = await state.get_data()
    users_id: list = data['performers_list']
    users_obj_list = [user_service.cache.get(int(user)) for user in users_id]

    await callback.message.edit_reply_markup(
        reply_markup=performers_keyboard(performers=users_obj_list, page=page)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("performer:select:"))
async def performer_select_handler(callback: CallbackQuery, state: FSMContext, user_service: UserService):
    """Обработка выбора исполнителя (прессбатн)"""
    try:
        user_id = int(callback.data.split(":")[2])
    except:
        await callback.answer("Ошибка при выборе исполнителя", show_alert=True)
        return

    # Сохраняем в FSM
    user = user_service.cache.get(user_id)
    await state.update_data(
        performer_id=user_id,
        performer_name=user.full_name(),  # полное имя
    )

    await flows.show_selected(callback, state, 'performer')  # делегируем отображение в flow
    await callback.answer()


@router.callback_query(F.data == "performer:back")
async def template_back_handler(callback: CallbackQuery, state: FSMContext, user_service: UserService):
    """Вернуться на этап выбора исполнителя"""
    data = await state.get_data()
    users_id: list = data['performers_list']
    users_obj_list = [user_service.cache.get(int(user)) for user in users_id]

    await callback.message.edit_reply_markup(
        reply_markup=performers_keyboard(performers=users_obj_list, page=0)
    )
    await callback.answer()


@router.callback_query(F.data == "performer:continue")
async def performer_continue_handler(callback: CallbackQuery, state: FSMContext):
    """Перейти на этап выбора типа задачи"""

    await flows.show_priority_selection(callback, state)
    await callback.answer()
