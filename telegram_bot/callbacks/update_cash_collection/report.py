import io
import datetime

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, BufferedInputFile
from utils.cash_collection_report import build_report 
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from telegram_bot.flows.cash_collection import show_cities_selection
from telegram_bot.services.template_service import TemplateService
from telegram_bot.services.cash_collection_service import CashCollectionService

router = Router()


@router.callback_query(F.data.startswith("cash_collection_report"))
async def remove_sheduler_task(callback: CallbackQuery, 
                               state: FSMContext,
                               cash_collection_service: CashCollectionService):
    """Формирует xlsx-отчёт за последние 30 дней и отправляет файлом в чат"""

    since = datetime.datetime.now() - datetime.timedelta(days=30)
    rows = await cash_collection_service.task_database.get_completed_since(since)

    if not rows:
        return await callback.message.edit_text(
            text="<b>Нет данных за последние 30 дней\n/menu</b>",
            reply_markup=None, 
            parse_mode="HTML"
        )


    buffer = io.BytesIO()
    build_report(rows, buffer)
    buffer.seek(0)

    file = BufferedInputFile(
        buffer.read(),
        filename="cash_collection_report.xlsx",
    )

    await callback.message.answer_document(file, caption="Отчёт за последние 30 дней")
    await callback.answer()