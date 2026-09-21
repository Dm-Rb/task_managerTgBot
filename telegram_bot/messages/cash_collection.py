from aiogram.fsm.context import FSMContext
from telegram_bot.models.cash_collection_task import ScheduledCashCollectionTask
from telegram_bot.services.template_service import TemplateService


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

def schedule_task_message_by_schedule_task_obj(schedule_task: ScheduledCashCollectionTask,                                               
                                               template_service: TemplateService,
                                               user_tg_id: int or None=None) -> str:
    """
    Генерирует сообщение с информацией о задаче на основе объекта ScheduledCashCollectionTask.
    Показывает только те поля, которые не являются None или пустыми.
    """

    lines = []
    lines.append(f"<b>Город:</b> <i>{schedule_task.city}</i>")
    
    points: list = template_service.get_points_by_city_id(schedule_task.city_id)
    if points:        
        # формируем текст для отображения пользователю
        points_text = ""
        for item in points:
            points_text += f"📍 <i>{template_service.adreses[item.adress_id].adress}, {template_service.points[item.id].point};</i>\n"
        points_text = points_text.strip('\n')
    else:
        points_text = "В текущем городе нет точек"
    lines.append(points_text)
    
    
    if user_tg_id:
        if hasattr(schedule_task, 'creator_id') and schedule_task.creator_id:
            lines.append(f"<b>Поставил(а) задачу:</b> <i>{'Вы' if schedule_task.creator_id == user_tg_id else schedule_task.creator_name}</i>")

    if hasattr(schedule_task, 'performer_name') and schedule_task.performer_name:
        lines.append(f"<b>Исполнитель:</b> <i>{schedule_task.performer_name}</i>")  

    # === Описание ===
    if hasattr(schedule_task, 'description') and schedule_task.description:
        desc = schedule_task.description
        if len(desc) > 400:
            desc = desc[:397] + "..."
        lines.append(f"<b>Описание:</b> <i>{desc}</i>")
        
    if hasattr(schedule_task, 'every_n_days') and schedule_task.every_n_days:
        lines.append(f"<b>Повторять каждые:</b> <i>{str(schedule_task.every_n_days)} дня(ей)</i>")

    return "\n".join(lines)