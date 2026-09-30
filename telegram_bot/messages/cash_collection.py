from aiogram.fsm.context import FSMContext
from telegram_bot.models.cash_collection_task import ScheduledCashCollectionTask
from telegram_bot.services.template_service import TemplateService
from telegram_bot.models.cash_collection_task import CashCollectionTask, CashCollectionPoint


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

def new_cash_collection_task_for_crearot(cash_collection_tasks: CashCollectionTask) -> str:
    message = f"💬 Сотрудник <b>{cash_collection_tasks.performer_name}</b> получил уведомление о необходимости проведения инкассации " 
    message += f"в городе <b>{cash_collection_tasks.city}</b> из пунктов:\n"
    for point in cash_collection_tasks.points:
        message += f"📍 <i>{point.adress}, {point.point};</i>\n"
    
    message += "Текущий статус задач можно посмотреть перейдя в главном меню бота в раздел <b>|💰 Инкассация</b>| <b>></b> <b>|📒 Список активных задач|</b> "
    message += "или отправив боту комманду \n/show_cash_tasks"
    return message
 
def new_cash_collection_task_for_performer(cash_collection_tasks: CashCollectionTask) -> str:
    message = f"💬 Вам необходимо провести инкассацию в городе <b>{cash_collection_tasks.city}</b> " 
    message += f"из пунктов:\n"
    for point in cash_collection_tasks.points:
        message += f"📍 {point.adress}, {point.point};\n"
    
    message += "Подробности задачи можно посмотреть открыв меню бота в разделе <b>|💰 Инкассация|</b> "
    message += "или отправив боту комманду /show_cash_tasks"
    return message

def show_active_tasks_for_crearot(cash_collection_tasks: CashCollectionTask) -> str:
    message = f"<b>Город:</b> {cash_collection_tasks.city}\n" 
    
    points_sorted = sorted(cash_collection_tasks.points, key=lambda point: point.status)
    status_emoji = {
        "В процессе": "🟡",
        "Выполнена": "🟢",
    }
    message += f"📍 <b>Пункты:</b>\n"
    for point in points_sorted:
        emoji = status_emoji.get(point.status, "⬜")
        message += f"{emoji} {point.status} > <i>{point.adress}, {point.point}</i>;\n"
        
    message += f"<b>Исполнитель:</b> {cash_collection_tasks.performer_name}\n"
    message += f"<b>Созданно в:</b> {str(cash_collection_tasks.created_at)}\n"
    message += f"<b>Описание:</b> {cash_collection_tasks.description}\n"

    return message

def show_active_tasks_for_perfomer(cash_collection_tasks: CashCollectionTask) -> str:
    message = "💰 Проведите инкассацию автоматов\n"
    message += f"<b>🏢 Город:</b> {cash_collection_tasks.city}\n" 
    message += f"<b>Описание:</b> {cash_collection_tasks.description}\n"
    message += f"Следуйте в один из пунктов, затем нажмите соответствующую кнопку:\n"

    return message

def remove_tasks_for_perfomer(cash_collection_tasks: CashCollectionTask) -> str:  
    message = f"💬 Ваши задачи по проведению инкассации из пунктов в городе <b>{cash_collection_tasks.city}</b> были отменены Администратором" 

    return message

def start_point(point: CashCollectionPoint) -> str:  
    message = f"В данный момент вы должны находиться в пункте 📍 <b>{point.adress}, {point.point}</b>.\n"
    message +=  "Отправьте боту фото показателей автомата ДО начала работ, после чего проведите инкассацию.\n/cancel - отмена\n" 
    message += "🔻📸🔻"
    return message

def resume_point() -> str:  
    message =  "Проведите инкассацию, затем отправьте боту фото ПОСЛЕ проведения работ.\n/cancel - отмена\n" 
    message += "🔻📸🔻"
    return message

def show_complite_point(point: CashCollectionPoint) -> str:  
    message = f"Завершить задачу по инкассации пункта 📍 <b>{point.adress}, {point.point}</b>?"
    return message

def completed_point_for_creator_msg(task: CashCollectionTask, point):
    message = f"💰 Сотрудник <b>{task.performer_name}</b> выполнил инкассацию\n"
    message += f"<b>Город:</b> {task.city}\n"
    message += f"<b>Пункт:</b> {point.adress}, {point.point}\n"
    message += f"<b>Комментарий:</b> {point.comment}\n"
    return message

def remaining_points_for_perfomer(points: list):
    message = f"<b>Осталось {str(len(points))} пунктов:</b>\n"
    for point in points:
        message += f"📍 <i>{point.adress}, {point.point}</i>;\n"
    message += "/show_cash_tasks"
    return message