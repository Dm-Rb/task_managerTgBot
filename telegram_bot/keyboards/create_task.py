from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup
from telegram_bot.models.task import TaskTemplate, TaskPriority, TaskType
from telegram_bot.models.group import Group
from telegram_bot.models.user import User


PAGE_SIZE = 10


def _add_pagination_buttons(page: int, end: int, arrow: list, builder: InlineKeyboardBuilder, callback_data_prefix: str):
    """Добавление кнопок для пагинации к клавиатурам"""
    pagination_buttons = []

    if page > 0:
        pagination_buttons.append(
            ("⬅️ Назад", f"{callback_data_prefix}:page:{page - 1}")
        )

    if end < len(arrow):
        pagination_buttons.append(
            ("➡️ Вперёд", f"{callback_data_prefix}:page:{page + 1}")
        )
    for text, callback_data in pagination_buttons:
        builder.button(
            text=text,
            callback_data=callback_data
        )
    return pagination_buttons


def task_templates_keyboard(task_templates: list[TaskTemplate], page: int = 0) -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()

    # отдельная кнопка создания шаблона
    builder.button(text="➕ Создать новый шаблон", callback_data="task_template:create")

    # фрагментируем список для пагинации
    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    current_templates = task_templates[start:end]  # срез

    # создаём кнопки из объектов TaskTemplate списка current_templates
    for index, template in enumerate(current_templates, start=start):
        builder.button(
            text=template.title,
            callback_data=f"task_template:select:{index}"
        )

    # добавить кнопки пагинации Назад\Вперёд в эту клавиатуру
    pagination_buttons = _add_pagination_buttons(page, end, task_templates, builder, 'task_template')
    rows = [1]

    rows.extend([1] * len(current_templates))

    if pagination_buttons:
        rows.append(len(pagination_buttons))

    builder.adjust(*rows)

    return builder.as_markup()


def groups_keyboard(groups: list[Group], page: int = 0) -> InlineKeyboardMarkup:
    """Инлайн-клавиатура для выбора группы"""
    builder = InlineKeyboardBuilder()

    # фрагментируем список для пагинации
    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    current_groups = groups[start:end]  # срез

    # создаём кнопки из объектов Group списка current_groups
    for index, group in enumerate(current_groups, start=start):
        builder.button(
            text=group.title,
            callback_data=f"group:select:{group.tg_id}"
        )
    # добавить кнопки пагинации Назад\Вперёд в эту клавиатуру
    pagination_buttons = _add_pagination_buttons(page, end, groups, builder, 'group')

    rows = [1] * len(current_groups)

    if pagination_buttons:
        rows.append(len(pagination_buttons))  # кнопки пагинации в одной строке

    builder.adjust(*rows)

    return builder.as_markup()


def performers_keyboard(performers: list[User], page: int = 0) -> InlineKeyboardMarkup:
    """Инлайн-клавиатура выбора исполнителя"""

    builder = InlineKeyboardBuilder()

    start = page * PAGE_SIZE
    end = start + PAGE_SIZE

    current_performers = performers[start:end]

    for performer in current_performers:
        builder.button(
            text=performer.full_name(),
            callback_data=f"performer:select:{performer.tg_id}"
        )

    pagination_buttons = _add_pagination_buttons(page, end, performers, builder, 'performer')

    rows = [1] * len(current_performers)
    if pagination_buttons:
        rows.append(len(pagination_buttons))

    builder.adjust(*rows)

    return builder.as_markup()


def priority_keyboard() -> InlineKeyboardMarkup:
    """Инлайн клавиатура с выбром приоритета задачи"""
    builder = InlineKeyboardBuilder()
    for index, priority in enumerate(TaskPriority.get_all()):
        builder.button(
            text=priority,
            callback_data=f"priority:select:{str(index)}"
        )
    builder.adjust(1)

    return builder.as_markup()


def task_type_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text=f"📌 {TaskType.ONCE.value}",
        callback_data="task_type:once"
    )
    builder.button(
        text=f"🔄 {TaskType.RECURRING.value}",
        callback_data="task_type:recurring"
    )

    builder.adjust(1)

    return builder.as_markup()


def task_type_recurrence_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text=f"Каждый день",
        callback_data="recurrence_task:repeat:1"
    )
    builder.button(
        text=f"Задать интервал дней",
        callback_data="recurrence_task:repeat:set"
    )

    builder.adjust(1)

    return builder.as_markup()


def confirm_or_back_keyboard(callback_data_prefix: str) -> InlineKeyboardMarkup:
    """Дополнительная клавиатура для подтверждения выбора\возвращения на предыдущий шаг"""

    builder = InlineKeyboardBuilder()
    builder.button(
        text="⬅️ Назад",
        callback_data=f"{callback_data_prefix}:back"
    )
    builder.button(
        text="Подтвердить",
        callback_data=f"{callback_data_prefix}:continue"
    )
    builder.adjust(2)

    return builder.as_markup()


def confirm_create_new_task() -> InlineKeyboardMarkup:
    """Подтверждение или Отмена создания задачи"""
    builder = InlineKeyboardBuilder()
    builder.button(
        text="✅ Создать задачу",
        callback_data="new_task:create"
    )
    builder.button(
        text="❌ Отменить",
        callback_data="new_task:cancel"
    )
    builder.adjust(2)

    return builder.as_markup()