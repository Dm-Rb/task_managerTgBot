from aiogram.fsm.context import FSMContext
from telegram_bot.models.task import Task


async def get_task_creation_message_by_state_data(state: FSMContext) -> str:
    """
    Генерирует сообщение с текущим состоянием создания задачи.
    Показывает только те поля, которые уже заполнены.
    """
    data = await state.get_data()

    lines = []

    # === Задача (Title) ===
    if template_title := data.get("template_title"):
        lines.append(f"<b>Задача:</b> <i>{template_title}</i>")

    # === Описание ===
    if template_description := data.get("template_description"):
        desc = template_description
        if len(desc) > 400:
            desc = desc[:397] + "..."
        lines.append(f"<b>Описание:</b> <i>{desc}</i>")

    # === Адрес ===
    if address := data.get("address"):
        lines.append(f"<b>Адрес:</b> <i>{address}</i>")

    # === Группа ===
    if group_title := data.get("group_title"):
        lines.append(f"<b>Группа:</b> <i>{group_title}</i>")

    # === Исполнитель ===
    if performer_name := data.get("performer_name"):
        lines.append(f"<b>Исполнитель:</b> <i>{performer_name}</i>")

    # === Приоритет ===
    if priority := data.get("priority"):
        # Добавляем эмодзи здесь, при отображении
        priority_emoji = {
            "Обычный": "🟢",
            "Высокий": "🟡",
            "Срочный": "🔴"
        }.get(priority, "")

        priority_text = f"{priority_emoji} {priority}" if priority_emoji else priority
        lines.append(f"<b>Приоритет:</b> <i>{priority_text}</i>")

    # === Тип задачи ===
    if task_type := data.get("task_type"):
        type_emoji = {
            "Разово": "📌",
            "По расписанию": "🔄"
        }.get(task_type, "")

        type_text = f"{type_emoji} {task_type}" if type_emoji else task_type
        lines.append(f"<b>Тип задачи:</b> <i>{type_text}</i>")
    if task_type := data.get("every_n_days"):
        lines.append(f"<b>Повторяется раз в:</b> <i>{str(task_type)} дней</i>")

    return "\n".join(lines)


def get_notification_task_message(type_: str, task: Task) -> str or None:
    """Обёртка для get_task_message_by_task_obj. Подставляет текст с типом уведомления в начало сообщения"""
    if type_ == "new":
        text = "🆕 <b>Новая задача</b>\n\n"
    elif type_ == "process":
        text = "🆙 <b>Сотрудник приступил к выполнению задачи</b>\n\n"
    elif type_ == "completed":
        text = "🏁 <b>Задача выполнена</b>\n\n"
    elif type_ == "cancelled":
        text = "❌ <b>Задача была отменена создателем</b>\n\n"

    else:
        return
    return text + get_task_message_by_task_obj(task)


def get_task_message_by_task_obj(task: Task) -> str:
    """
    Генерирует сообщение с информацией о задаче на основе объекта Task.
    Показывает только те поля, которые не являются None или пустыми.
    """
    lines = []

    # === Название задачи ===
    if hasattr(task, 'title') and task.title:
        lines.append(f"<b>Задача:</b> <i>{task.title}</i>")

    # === Статус ===
    if hasattr(task, 'status') and task.status:
        status_emoji = {
            "Новая": "🟢",
            "В процессе": "🟡",
            "Выполнено": "✅",
            "Отменена": "❌"
        }.get(task.status.value, "")

        status_text = f"{status_emoji} {task.status}" if status_emoji else task.status
        lines.append(f"<b>Статус:</b> <i>{status_text}</i>")

    # === Тип задачи ===
    if hasattr(task, 'task_type') and task.task_type:
        type_emoji = {
            "Разово": "📌",
            "По расписанию": "🔄"
        }.get(task.task_type, "")

        type_text = f"{type_emoji} {task.task_type}" if type_emoji else task.task_type
        lines.append(f"<b>Тип задачи:</b> <i>{type_text}</i>")
    # === Время реагирования ===
    if (
            hasattr(task, 'accepted_at') and task.accepted_at and
            hasattr(task, 'created_at') and task.created_at
    ):
        delta = task.accepted_at - task.created_at

        total_seconds = int(delta.total_seconds())

        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60

        reaction_time = f"{hours:02}:{minutes:02}"
        if reaction_time == '00:00':
            reaction_time = 'Мгновенно'
        lines.append(
            f"<b>Время реагирования:</b> <i>⏱ {reaction_time}</i>"
        )

    # === Время выполнения ===
    if (
            hasattr(task, 'accepted_at') and task.accepted_at and
            hasattr(task, 'completed_at') and task.completed_at
    ):
        delta = task.completed_at - task.accepted_at

        total_seconds = int(delta.total_seconds())

        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60

        execution_time = f"{hours:02}:{minutes:02}"

        if execution_time == '00:00':
            execution_time = 'Мгновенно'

        lines.append(
            f"<b>Время выполнения:</b> <i>⏱ {execution_time}</i>"
        )

    # === Группа ===
    if hasattr(task, 'group_title') and task.group_title:
        lines.append(f"<b>Группа:</b> <i>{task.group_title}</i>")

    # === Исполнитель ===
    if hasattr(task, 'performer_name') and task.performer_name:
        lines.append(f"<b>Исполнитель:</b> <i>{task.performer_name}</i>")

    # === Приоритет ===
    if hasattr(task, 'priority') and task.priority:
        # Исправленный словарь - поддерживает значения с эмодзи и без
        priority_emoji = {
            "Обычный": "🟢",
            "Высокий": "🟡",
            "Срочный": "🔴",
            "Низкий": "🔵",
            "Средний": "🟠"
        }.get(task.priority, "")

        # Если эмодзи уже есть в строке, не добавляем повторно
        if any(emoji in task.priority for emoji in ["🟢", "🟡", "🔴", "🟠", "🔵"]):
            priority_text = task.priority
        else:
            priority_text = f"{priority_emoji} {task.priority}" if priority_emoji else task.priority

        lines.append(f"<b>Приоритет:</b> <i>{priority_text}</i>")

    if hasattr(task, 'address') and task.address:
        lines.append(f"<b>Адрес:</b> <i>{task.address}</i>")

    # === Описание ===
    if hasattr(task, 'description') and task.description:
        desc = task.description
        if len(desc) > 400:
            desc = desc[:397] + "..."
        lines.append(f"<b>Описание:</b> <i>{desc}</i>")

    return "\n".join(lines)