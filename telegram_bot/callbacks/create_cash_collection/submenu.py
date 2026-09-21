from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from telegram_bot.keyboards.cash_collection import cities_keyboard
from telegram_bot.flows.cash_collection import show_cities_selection
from telegram_bot.services.template_service import TemplateService
from telegram_bot.services.cash_collection_service import CashCollectionService


router = Router()


@router.callback_query(F.data.startswith("cash_collection:create_sheduler_task"))
async def create_sheduler_task(callback: CallbackQuery, 
                               state: FSMContext, 
                               template_service: TemplateService):

    await show_cities_selection(callback, state, template_service, "cash_collection_cities_create")