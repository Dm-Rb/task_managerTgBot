from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup

from telegram_bot.models.task import TaskStatus


def performer_task_keyboard(task_id: str, status: TaskStatus) -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()
    if status == TaskStatus.CREATED:

        builder.button(
            text="✅ Взять задачу",
            callback_data=f"task:accept:{task_id}"
        )

    elif status == TaskStatus.IN_PROGRESS:

        builder.button(
            text="🏁 Завершить задачу",
            callback_data=f"task:complete:{task_id}"
        )

    builder.adjust(1)

    return builder.as_markup()

def creator_task_keyboard(task_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text="❌ Отменить задачу",
        callback_data=f"task:cancel:{task_id}"
    )

    builder.adjust(1)

    return builder.as_markup()
