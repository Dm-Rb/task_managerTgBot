from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from telegram_bot.services.cash_collection_service import CashCollectionService
from telegram_bot.services.template_service import TemplateService
from telegram_bot.messages.cash_collection import schedule_task_message_by_schedule_task_obj


router = Router()


@router.callback_query(F.data.startswith("shedule_cash_collection:create"))
async def create_new_scheduler_task_handler(callback: CallbackQuery, 
                                            state: FSMContext,
                                            cash_collection_service: CashCollectionService,
                                            template_service: TemplateService):
    state_data = await state.get_data()
        
    sheduled_task = await cash_collection_service.create_shedule_task(
            city_id=state_data.get("city_id"),
            city=state_data.get("city"),
            description=state_data.get("description"),
            creator_id=callback.from_user.id,
            creator_name=callback.from_user.full_name,
            performer_id=state_data.get("performer_id"),
            performer_name=state_data.get("performer_name"),
            every_n_days=state_data.get("every_n_days"),
        )
    prew_text = "🆕 <b>Вы создали новую конфигурацию задачи по инкассации. Эта конфигурация будет использоваться для автоматического создания задач через заданные промежутки времени.</b>\n\n"
    await callback.message.edit_text(
        text=prew_text + schedule_task_message_by_schedule_task_obj(sheduled_task, template_service, callback.from_user.id),
        reply_markup=None,
        parse_mode="HTML"
    )
    await callback.answer("✅ Шаблон задачи создан")
    await state.clear()


@router.callback_query(F.data.startswith("shedule_cash_collection:cancel"))
async def cancel_new_scheduler_task_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        text="❌ Отменено",
        reply_markup=None,
        parse_mode="HTML"
    )

async def is_exist_scheduler_task_by_city_id(cash_collection_service: CashCollectionService, city_id: int):
    shedule_tasks: list = await cash_collection_service.get_shedule_tasks()
    for item in shedule_tasks:
        if item.city_id == city_id:
            return True
    return False
    
