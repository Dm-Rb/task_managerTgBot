from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


async def logout_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Да"),
                KeyboardButton(text="Нет"),
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard
