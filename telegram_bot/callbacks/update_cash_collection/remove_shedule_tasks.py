from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from telegram_bot.services.cash_collection_service import CashCollectionService
from telegram_bot.services.template_service import TemplateService
from telegram_bot.messages.cash_collection import schedule_task_message_by_schedule_task_obj
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from telegram_bot.keyboards.cash_collection import cities_keyboard
from telegram_bot.keyboards.create_task import confirm_or_back_keyboard
from telegram_bot.flows.cash_collection import show_cities_selection
from telegram_bot.flows.cash_collection import show_performer_selection
from telegram_bot.services.template_service import TemplateService
from database.models.point import PointTable
from telegram_bot.services.user_service import UserService
from telegram_bot.messages.cash_collection import cash_collection_creation_message_by_state_data

router = Router()


@router.callback_query(F.data.startswith("cash_collection_cities:page:"))
async def cash_collection_cities_pagination(callback: CallbackQuery, template_service: TemplateService):
    """Пагинация шаблонов с городами"""
    try:
        page = int(callback.data.split(":")[2])
    except:
        await callback.answer("Ошибка", show_alert=True)
        return

    await callback.message.edit_reply_markup(
        reply_markup=cities_keyboard(template_service.cities, page=page)
    )

    await callback.answer()


@router.callback_query(F.data.startswith("cash_collection_cities:select:"))
async def cash_collection_cities_select(callback: CallbackQuery,  state: FSMContext, template_service: TemplateService):
    """Обработка нажатия на кнопку города"""
    try:
        city_key = int(callback.data.split(":")[2])

    except:
        await callback.answer("Ошибка", show_alert=True)
        return

    points: list[PointTable] = template_service.get_points_by_city_id(city_key)
    if not points:
        return await callback.answer(text="Нет точек для выбранного города")
    # формируем текст для отображения пользователю
    points_text = ""
    for item in points:
        points_text += f"📍 <i>{template_service.adreses[item.adress_id].adress}, {template_service.points[item.id].point};</i>\n"
    points_text = points_text.strip('\n')
    
    await state.update_data(
        city_id=city_key, 
        city=template_service.cities[city_key].city,
        points_text=points_text
        )
    message_ = await cash_collection_creation_message_by_state_data(state)
    await callback.message.edit_text(
        text=message_,
        reply_markup=confirm_or_back_keyboard("cash_collection_cities", None), 
        parse_mode="HTML"
    )

router = Router()


@router.callback_query(F.data.startswith("cash_collection:remove_sheduler_tasks"))
async def cancel_new_scheduler_task_handler(callback: CallbackQuery, cash_collection_service: CashCollectionService):
    await callback.message.delete()
    shedule_tasks: list = await cash_collection_service.get_shedule_tasks()
    for item in shedule_tasks:
        pass


