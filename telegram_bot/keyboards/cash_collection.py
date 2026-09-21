from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup
from telegram_bot.keyboards.create_task import PAGE_SIZE, _add_pagination_buttons

from aiogram.types import InlineKeyboardMarkup
from database.models.city import CityTable
from telegram_bot.models.user import User



def cash_collection_submenu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text=f"Создать шаблон задачи",
        callback_data="cash_collection:create_sheduler_task"
    )
    builder.button(
        text="Удалить шаблон задачи",
        callback_data="cash_collection:remove_sheduler_task"
    )
    builder.button(
        text="Список активных задач",
        callback_data="cash_collection:task_list"
    )

    builder.adjust(1)

    return builder.as_markup()


def cities_keyboard(cities: dict[int, CityTable], page: int = 0) -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()

    start = page * PAGE_SIZE
    end = start + PAGE_SIZE

    current_cities_keys = list(cities.keys())[start:end]
    # шаблоны адресов

    for city_key in current_cities_keys:
        builder.button(
            text=cities[city_key].city,
            callback_data=f"cash_collection_cities:select:{str(city_key)}"
        )

    # пагинация
    nav_buttons = []

    if page > 0:
        nav_buttons.append(
            ("⬅️", f"cash_collection_cities:page:{page - 1}")
        )

    if end < len(list(cities.keys())):
        nav_buttons.append(
            ("➡️", f"cash_collection_cities:page:{page + 1}")
        )

    for text, callback_data in nav_buttons:
        builder.button(
            text=text,
            callback_data=callback_data
        )

    builder.adjust(1)

    return builder.as_markup()

def performers_keyboard(performers: list[User], page: int = 0) -> InlineKeyboardMarkup:
    """Инлайн-клавиатура выбора исполнителя"""

    builder = InlineKeyboardBuilder()

    start = page * PAGE_SIZE
    end = start + PAGE_SIZE

    current_performers = performers[start:end]
    ROLES = {2: "🧑🏻‍💻", 1: "👨🏻‍💼"}
    for performer in current_performers:
        try:
            performer_name = performer.full_name()
        except:
            performer_name = performer.first_name
        builder.button(
            text=f"{ROLES[int(performer.role)]} {performer_name}",
            callback_data=f"сash_collection_performer:select:{performer.tg_id}"
        )

    pagination_buttons = _add_pagination_buttons(page, end, performers, builder, 'сash_collection_performer')

    rows = [1] * len(current_performers)
    if pagination_buttons:
        rows.append(len(pagination_buttons))

    builder.adjust(*rows)

    return builder.as_markup()

def confirm_create_new_cash_collection(prefix: str) -> InlineKeyboardMarkup:
    """Подтверждение или Отмена создания задачи инкассации"""
    builder = InlineKeyboardBuilder()
    builder.button(
        text="❌ Отменить",
        callback_data=f"{prefix}:cancel"
    )
    builder.button(
        text="✅ Создать задачу",
        callback_data=f"{prefix}:create"
    )
    builder.adjust(2)

    return builder.as_markup()