from aiogram import Router, F
from aiogram.types import CallbackQuery
from telegram_bot.keyboards.cash_collection import performers_keyboard
from telegram_bot.keyboards.create_task import confirm_or_back_keyboard

from aiogram.fsm.context import FSMContext
from telegram_bot.flows.create_task import show_selected
from telegram_bot.flows.cash_collection import show_performer_selection
from telegram_bot.states import CreateСashColletionStates

from telegram_bot.services.user_service import UserService
from telegram_bot.messages.cash_collection import cash_collection_creation_message_by_state_data


router = Router()


@router.callback_query(F.data.startswith("сash_collection_performer:page:"))
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


@router.callback_query(F.data.startswith("сash_collection_performer:select:"))
async def performer_select_handler(callback: CallbackQuery, state: FSMContext, user_service: UserService):
    """Обработка выбора исполнителя (прессбатн)"""
    try:
        user_id = int(callback.data.split(":")[2])
    except:
        await callback.answer("Ошибка при выборе исполнителя", show_alert=True)
        return
    
    user = user_service.cache.get(user_id)

    # Сохраняем в FSM
    await state.update_data(
        performer_id=user_id,
        performer_name=user.full_name()
    )
    
    message_ = await cash_collection_creation_message_by_state_data(state)
    await callback.message.edit_text(
        text=message_,
        reply_markup=confirm_or_back_keyboard('сash_collection_performer'),  # префикс для коллбеков
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "сash_collection_performer:back")
async def template_back_handler(callback: CallbackQuery, state: FSMContext, user_service: UserService):
    """Вернуться на этап выбора исполнителя"""
    performers = user_service.get_performers(callback.from_user.id)
    if not performers:  # если нет исполнителей - показать сообщение и вернуться на этап выбора группы
        return await callback.answer(text="Нет ни одного исполнителя")

    # Сохраняем список user.tg_id для более быстрого получения списка исполнителей в performer_page_handler
    await state.update_data(performers_list=[p.tg_id for p in performers])  # list[int]

    await show_performer_selection(callback, performers)
    


@router.callback_query(F.data == "сash_collection_performer:continue")
async def performer_continue_handler(callback: CallbackQuery, state: FSMContext):
    """Перейти на этап ввода описания"""
    # удаляем сообщение целиком
    await callback.message.delete()
    # переводим FSM
    
    # отправляем новое сообщение
    await callback.message.answer(
        "Введите описание для задач инкассации 👇🏻"
    )
    await state.set_state(CreateСashColletionStates.waiting_description)
    
