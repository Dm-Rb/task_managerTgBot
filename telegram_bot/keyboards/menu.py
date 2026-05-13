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

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=True,
        selective=True
    )