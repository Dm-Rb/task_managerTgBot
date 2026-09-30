from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup
from telegram_bot.keyboards.create_task import PAGE_SIZE, _add_pagination_buttons
from aiogram.types import InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup
from database.models.city import CityTable
from telegram_bot.models.user import User
from telegram_bot.models.cash_collection_task import CashCollectionTask


def cash_collection_submenu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text=f"🆕 Создать конфигурацию задачи",
        callback_data="cash_collection:create_sheduler_task"
    )
    builder.button(
        text="🗑 Удалить конфигурацию задачи",
        callback_data="cash_collection:remove_sheduler_task"
    )
    builder.button(
        text="📒 Список активных задач",
        callback_data="cash_collection:task_list"
    ),
    builder.button(
        text="📊 Отчёт по за последние 30 дней",
        callback_data="cash_collection_report"
    )
        
    builder.adjust(1)

    return builder.as_markup()


def cities_keyboard(cities: dict[int, CityTable], callback_prefix: str, page: int = 0) -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()

    start = page * PAGE_SIZE
    end = start + PAGE_SIZE

    current_cities_keys = list(cities.keys())[start:end]
    # шаблоны адресов

    for city_key in current_cities_keys:
        builder.button(
            text=cities[city_key].city,
            callback_data=f"{callback_prefix}:select:{str(city_key)}"
        )

    # пагинация
    nav_buttons = []

    if page > 0:
        nav_buttons.append(
            ("⬅️", f"{callback_prefix}:page:{page - 1}")
        )

    if end < len(list(cities.keys())):
        nav_buttons.append(
            ("➡️", f"{callback_prefix}:page:{page + 1}")
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
    if not current_performers:
        return None
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

def remove_shedule_task(shedule_task_id: str) -> InlineKeyboardMarkup:
    """Подтверждение или Отмена создания задачи инкассации"""
    builder = InlineKeyboardBuilder()
    builder.button(
        text="❌ Удалить конфигурацию",
        callback_data=f"cash_collection_shedule_task:ask_cnf_rm:{shedule_task_id}"
    )
    builder.adjust(2)

    return builder.as_markup()

def confirm_keyboard(action: str, object_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text="✅ Да",
        callback_data=f"{action}:{object_id}:yes"
    )

    builder.button(
        text="❌ Нет",
        callback_data=f"{action}:{object_id}:no"
    )

    builder.adjust(2)
    return builder.as_markup()

def remove_task(task_id: str) -> InlineKeyboardMarkup:
    """Удаление активных задач по инкассации"""
    builder = InlineKeyboardBuilder()
    builder.button(
        text="❌ Снять все задачи",
        callback_data=f"cash_collection_task:ask_cnf_rm:{task_id}"
    )
    builder.adjust(2)

    return builder.as_markup()



def show_points_for_perfomer(cash_collection_task: CashCollectionTask, page: int = 0) -> InlineKeyboardMarkup:
    """Создать кнопки с пунктами для инкассации"""
    CALLBACK_PREFIX = "comptile_cc_task"
    parent_id = cash_collection_task.parent_id
    builder = InlineKeyboardBuilder()
    points = [p for p in cash_collection_task.points if p.status == "В процессе"]

    # защита от выхода за границы
    max_page = max((len(points) - 1) // PAGE_SIZE, 0)
    page = min(max(page, 0), max_page)

    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    current_points = points[start:end]

    for point in current_points:
        builder.button(
            text=f"📌 {point.adress} - {point.point}",
            callback_data=f"{CALLBACK_PREFIX}:select:{parent_id}:{point.id}",
        )

    # пагинация вручную, с parent_id внутри callback_data
    pagination_buttons = []
    if page > 0:
        pagination_buttons.append(
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=f"{CALLBACK_PREFIX}:page:{parent_id}:{page - 1}",
            )
        )
    if end < len(points):
        pagination_buttons.append(
            InlineKeyboardButton(
                text="➡️ Вперёд",
                callback_data=f"{CALLBACK_PREFIX}:page:{parent_id}:{page + 1}",
            )
        )
    for btn in pagination_buttons:
        builder.add(btn)

    # каждая точка в своём ряду, стрелки вместе в одном
    sizes = [1] * len(current_points)
    if pagination_buttons:
        sizes.append(len(pagination_buttons))
    if sizes:
        builder.adjust(*sizes)

    return builder.as_markup()

