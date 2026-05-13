from aiogram import Router, F
from aiogram.types import CallbackQuery

from telegram_bot.services.task_runtime_service import TaskRuntimeService
from telegram_bot.messages.task import get_task_message_by_task_obj
from telegram_bot.keyboards.update_task import performer_task_keyboard


router = Router()

@router.callback_query(F.data.startswith("task:complete:"))
async def accept_task_handler(callback: CallbackQuery, runtime_service: TaskRuntimeService):
    try:
        task_id = callback.data.split(":")[2]

    except Exception:
        await callback.answer(
            "Ошибка",
            show_alert=True
        )
        return

    # Обновляем задачу

    task = await runtime_service.accept_task(task_id)


    await callback.answer("Функционал для этой кнопки перерабатываятся в связи с багами")