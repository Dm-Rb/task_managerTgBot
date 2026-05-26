from aiogram import Router, F
from aiogram.types import Message
from aiogram.types.input_file import FSInputFile
from utils.xlsx_report import export_completed_tasks_report


router = Router()


@router.message(F.text == "📊 Отчёт по выполненным задачам")
async def completed_tasks_report_handler(message: Message, task_service):
    """
    Отправить XLSX отчёт
    по выполненным задачам
    """
    report_path = await export_completed_tasks_report(
        repository=task_service.task_database
    )
    report_file = FSInputFile(report_path)

    await message.answer_document(
        document=report_file,
        caption="📊 Отчёт по выполненным задачам за последние 30 дней"
    )