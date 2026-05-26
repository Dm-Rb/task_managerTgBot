from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton
)


def main_menu_keyboard(
    role: int
) -> ReplyKeyboardMarkup:
    """
    Главное меню пользователя

    role:
        1 -> сотрудник
        2 -> администратор
    """

    keyboard = []

    # ==========================================
    # Кнопки администратора
    # ==========================================

    if role == 2:

        keyboard.append([
            KeyboardButton(
                text="➕ Создать новую задачу"
            )
        ])

        keyboard.append([
            KeyboardButton(
                text="📅 Создать шаблон задачи по расписанию"
            )
        ])

        keyboard.append([
            KeyboardButton(
                text="🗓 Список всех активных задач"
            )
        ])

        keyboard.append([
            KeyboardButton(
                text="📆 Список шаблонов задач по-расписанию"
            )
        ])

    # ==========================================
    # Общие кнопки
    # ==========================================

    keyboard.append([
        KeyboardButton(
            text="📋 Мои задачи"
        )
    ])
    keyboard.append([
        KeyboardButton(
            text="🚪 Разлогиниться"
        )
    ])
    if role == 2:
        keyboard.append([
            KeyboardButton(
                text="📊 Отчёт по выполненным задачам"
            )
        ])

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=True,
        selective=True
    )