from aiogram import Router, F
from aiogram.types import CallbackQuery
from telegram_bot.keyboards.create_task import groups_keyboard
from aiogram.fsm.context import FSMContext
from telegram_bot.flows.create_task import show_selected, show_groups_selection, \
    show_no_performers_in_group, show_performer_selection
from telegram_bot.services.group_service import GroupService

router = Router()


@router.callback_query(F.data.startswith("group:page:"))
async def group_page_handler(callback: CallbackQuery, group_service: GroupService):
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
async def group_select_handler(callback: CallbackQuery, state: FSMContext, group_service: GroupService):
    """Обработка выбора группы (прессбатн)"""

    try:
        group_id = int(callback.data.split(":")[2])
    except:
        await callback.answer("Ошибка при выборе группы", show_alert=True)
        return
    # Сохраняем в FSM
    await state.update_data(
        group_id=group_id,
        topic_id=None,
        group_title=group_service.get_group_by_id(group_id).title,  # обращаемся к экземпляру класса GroupService
    )
    if len(callback.data.split(":")) >= 4:
        try:
            topic_id = int(callback.data.split(":")[3])
            group_service.get_topic(group_id, topic_id)
            await state.update_data(
                group_id=group_id,
                topic_id=topic_id,
                group_title=f"{group_service.get_group_by_id(group_id).title} / {group_service.get_topic(group_id, topic_id).title}"
                # обращаемся к экземпляру класса GroupService
            )
        except:
            pass

    # await show_selected(callback, state, 'group')  # делегируем отображение в flow
    await show_selected(callback, state, "group", "🗑 Удалить эту группу" if len(group_service.get_all_groups()) > 0 else None)
    await callback.answer()


@router.callback_query(F.data == "group:back")
async def group_back_handler(callback: CallbackQuery, state: FSMContext, group_service):
    """Вернуться на этап выбора группы"""
    await show_groups_selection(callback, state, group_service)

    await callback.answer()


@router.callback_query(F.data == "group:delete")
async def create_task_template(callback: CallbackQuery, state: FSMContext, group_service: GroupService):
    state_data = await state.get_data() # получить данные у далить через сервис
    if state_data.get('group_id', None):
        if state_data.get('topic_id', None):
            await group_service.remove_topic(state_data['group_id'], state_data['topic_id'])
        else:
            await group_service.remove_group(state_data['group_id'])
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





