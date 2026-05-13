from aiogram import Router, F
from aiogram.types import CallbackQuery
from telegram_bot.keyboards.create_task import groups_keyboard
from aiogram.fsm.context import FSMContext
from telegram_bot.flows.create_task import show_selected, show_groups_selection, \
    show_no_performers_in_group, show_performer_selection


router = Router(name="group")


@router.callback_query(F.data.startswith("group:page:"))
async def group_page_handler(callback: CallbackQuery, group_service):
    """Пагинация списка групп. Изменяет клавиатуру"""
    try:
        page = int(callback.data.split(":")[2])
    except:
        await callback.answer("Ошибка", show_alert=True)
        return

    groups: list = group_service.get_all_groups()
    keyboard = groups_keyboard(groups=groups, page=page)

    await callback.message.edit_reply_markup(reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("group:select:"))
async def group_select_handler(callback: CallbackQuery, state: FSMContext, group_service):
    """Обработка выбора группы (прессбатн)"""

    try:
        group_id = int(callback.data.split(":")[2])
    except:
        await callback.answer("Ошибка при выборе группы", show_alert=True)
        return

    # Сохраняем в FSM
    await state.update_data(
        group_id=group_id,
        group_title=group_service.get_group_by_id(group_id).title,  # обращаемся к экземпляру класса GroupService
    )

    await show_selected(callback, state, 'group')  # делегируем отображение в flow
    await callback.answer()


@router.callback_query(F.data == "group:back")
async def group_back_handler(callback: CallbackQuery, state: FSMContext, group_service):
    """Вернуться на этап выбора группы"""
    await show_groups_selection(callback, state, group_service)

    await callback.answer()


@router.callback_query(F.data == "group:continue")
async def group_continue_handler(callback: CallbackQuery, state: FSMContext, group_service, user_service):
    """Перейти на этап выбора исполнителя"""
    data = await state.get_data()
    group_id: int = int(data["group_id"])
    # получаем исполнителей через сервис (user.role == 1 которые состоят в группе group_id)
    performers = await user_service.get_performers_in_group(bot=callback.bot, group_id=group_id)

    if not performers:  # если нет исполнителей - показать сообщение и вернуться на этап выбора группы
        return await show_no_performers_in_group(callback, state, group_service, group_id)

    # Сохраняем список user.tg_id для более быстрого получения списка исполнителей в performer_page_handler
    await state.update_data(performers_list=[p.tg_id for p in performers])  # list[int]

    await show_performer_selection(callback, state, performers)





