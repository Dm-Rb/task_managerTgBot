from aiogram.fsm.context import FSMContext


async def cash_collection_creation_message_by_state_data(state: FSMContext) -> str:
    """
    Генерирует сообщение с текущим состоянием создания задачи инкасации.
    Показывает только те поля, которые уже заполнены.
    """
    data = await state.get_data()

    lines = []

    if city := data.get("city"):
        lines.append(f"<b>Город:</b> <i>{city}</i>")
        
    if points_text := data.get("points_text"):
        desc = points_text
        if len(desc) > 400:
            desc = desc[:397] + "..."
        lines.append(f"<b>Список точек, по которым необходимо выполнять инкассацию:</b> \n<i>{desc}</i>")

    if performer_name := data.get("performer_name"):
        lines.append(f"<b>Исполнитель:</b> <i>{performer_name}</i>")

    if description := data.get("description"):
        lines.append(f"<b>Описание:</b> <i>{description}</i>")
        
    if every_n_days := data.get("every_n_days"):
        lines.append(f"<b>Интервал:</b> <i>каждые {str(every_n_days)} дней</i>")

    return "\n".join(lines)