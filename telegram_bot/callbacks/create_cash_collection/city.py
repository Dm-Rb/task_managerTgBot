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
from telegram_bot.services.cash_collection_service import CashCollectionService

router = Router()


@router.callback_query(F.data.startswith("cash_collection_cities_create:page:"))
async def cash_collection_cities_pagination(callback: CallbackQuery, template_service: TemplateService):
    """Пагинация шаблонов с городами"""
    try:
        page = int(callback.data.split(":")[2])
    except:
        await callback.answer("Ошибка", show_alert=True)
        return

    await callback.message.edit_reply_markup(
        reply_markup=cities_keyboard(template_service.cities, "cash_collection_cities_create", page=page)
    )

    await callback.answer()


@router.callback_query(F.data.startswith("cash_collection_cities_create:select:"))
async def cash_collection_cities_select(callback: CallbackQuery,  
                                        state: FSMContext, 
                                        template_service: TemplateService,
                                        cash_collection_service: CashCollectionService):
    """Обработка нажатия на кнопку города"""
    try:
        city_key = int(callback.data.split(":")[2])

    except:
        await callback.answer("Ошибка", show_alert=True)
        return
    # Проверяем кеш с уже созданными шаблонами. Если есть шаблон с выбранным городом - сообщаем пользователю
    exist_scheduler_task: bool = await is_exist_scheduler_task_by_city_id(cash_collection_service, city_key)
    if exist_scheduler_task:
        await state.clear()
        await callback.message.edit_text(
        text=f"Для города {template_service.cities[city_key].city} уже создана конфигурация автоматического создания задач по инкассации",
        reply_markup=None
        )
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
        reply_markup=confirm_or_back_keyboard("cash_collection_cities_create", None), 
        parse_mode="HTML"
    )
    

@router.callback_query(F.data.startswith("cash_collection_cities_create:back"))
async def cash_collection_cities_back(callback: CallbackQuery, state: FSMContext, template_service: TemplateService):
    await show_cities_selection(callback, state, template_service, "cash_collection_cities_create")
    
    
@router.callback_query(F.data.startswith("cash_collection_cities_create:continue"))
async def cash_collection_cities_continue(callback: CallbackQuery, user_service: UserService):
    performers = user_service.get_performers(callback.from_user.id)
    await show_performer_selection(callback, performers)
    
async def is_exist_scheduler_task_by_city_id(cash_collection_service: CashCollectionService, city_id: int)->bool:
    """Вспомогательная функция. Проверяет все существующие конфигурации задач инкассации в кеше 
    и сверяет их city_id и переданным в аргументе. Возвращает булиево значение"""
    shedule_tasks: list = await cash_collection_service.get_shedule_tasks()
    if not shedule_tasks:
        return False
    for item in shedule_tasks:
        if item.city_id == city_id:
            return True
    return False