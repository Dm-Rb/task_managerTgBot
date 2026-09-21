from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from telegram_bot.services.cash_collection_service import CashCollectionService
from telegram_bot.services.template_service import TemplateService
from telegram_bot.messages.cash_collection import schedule_task_message_by_schedule_task_obj
from telegram_bot.keyboards.cash_collection import cities_keyboard, remove_shedule_task
from telegram_bot.messages.cash_collection import schedule_task_message_by_schedule_task_obj
from telegram_bot.keyboards.cash_collection import confirm_keyboard


router = Router()


@router.callback_query(F.data.startswith("cash_collection_cities_rm:page:"))
async def cash_collection_cities_pagination(callback: CallbackQuery, template_service: TemplateService):
    """Пагинация шаблонов с городами"""
    try:
        page = int(callback.data.split(":")[2])
    except:
        await callback.answer("Ошибка", show_alert=True)
        return

    await callback.message.edit_reply_markup(
        reply_markup=cities_keyboard(template_service.cities, "cash_collection_cities_rm", page=page)
    )

    await callback.answer()


@router.callback_query(F.data.startswith("cash_collection_cities_rm:select:"))
async def cash_collection_cities_select(callback: CallbackQuery,                                        
                                        template_service: TemplateService,
                                        cash_collection_service: CashCollectionService):
    """Обработка нажатия на кнопку города"""
    try:
        city_key = int(callback.data.split(":")[2])

    except:
        await callback.answer("Ошибка", show_alert=True)
        return
    # получаем список всех шаблонов из кеша и ищем совпадение по городу
    shedule_tasks: list = await cash_collection_service.get_shedule_tasks()
    for item in shedule_tasks:
        if item.city_id == city_key:
            # Формируем текст
            message_ = schedule_task_message_by_schedule_task_obj(item, template_service, callback.from_user.id)
            await callback.message.edit_text(
                text=message_,
                reply_markup=remove_shedule_task(item.id), 
                parse_mode="HTML"
            )
            return
    await callback.message.edit_text(
            text="<b>Нет конфигураций задач для этого города</b>",
            reply_markup=None, 
            parse_mode="HTML"
        )

@router.callback_query(F.data.startswith("cash_collection_shedule_task:ask_cnf_rm:"))
async def cancel_new_scheduler_task_handler(callback: CallbackQuery):
    schedule_task_id = callback.data.split(":")[2]
    await callback.message.edit_text(
        text="<b>Вы уверены, что хотите удалить эту конфигурацию?</b>",
        reply_markup=confirm_keyboard("confirm_cash_cllton_shdl_tsk", schedule_task_id), 
        parse_mode="HTML"
    )
    
@router.callback_query(F.data.startswith("confirm_cash_cllton_shdl_tsk"))
async def confirm_remove_yes(callback: CallbackQuery, cash_collection_service: CashCollectionService, state: FSMContext, ):
    action, scheduler_task_id, answer = callback.data.split(":")
    if answer == "yes":
        city = cash_collection_service.sheduled_tasks[scheduler_task_id].city
        await cash_collection_service.remove_shedule_task_by_id(scheduler_task_id)
        await callback.message.edit_text(
        text=f"<b>Конфигурация для создания задач инкассации по городу {city} была удалена...</b>",
        reply_markup=None, 
        parse_mode="HTML"
            )
        
    elif answer == "no":
         await callback.message.delete()        
    await state.clear()
    return





