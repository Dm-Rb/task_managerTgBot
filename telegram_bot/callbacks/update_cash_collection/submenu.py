from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from telegram_bot.keyboards.cash_collection import cities_keyboard
from telegram_bot.flows.cash_collection import show_cities_selection
from telegram_bot.services.template_service import TemplateService
from telegram_bot.services.cash_collection_service import CashCollectionService


router = Router()


@router.callback_query(F.data.startswith("cash_collection:remove_sheduler_task"))
async def remove_sheduler_task(callback: CallbackQuery, 
                               state: FSMContext, template_service: TemplateService,
                               cash_collection_service: CashCollectionService):
    shedule_tasks: list = await cash_collection_service.get_shedule_tasks()
    if not shedule_tasks:
            await callback.message.edit_text(
                text="<b>Список конфигураций задач по инкассации пуст</b>",
                reply_markup=None, 
                parse_mode="HTML"
            )
            return
    await show_cities_selection(callback, state, template_service, "cash_collection_cities_rm")