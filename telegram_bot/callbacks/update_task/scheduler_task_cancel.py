from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from telegram_bot.services.user_service import UserService
from telegram_bot.services.task_runtime_service import TaskRuntimeService
from telegram_bot.services.task_service import TaskService

from telegram_bot.messages.task import get_schedule_task_creation_message_by_state_schedule_task_obj
from telegram_bot.keyboards.update_task import performer_task_keyboard


router = Router()


@router.callback_query(F.data.startswith("scheduler_task:cancel:"))
async def accept_task_handler(callback: CallbackQuery, runtime_service: TaskRuntimeService, task_service: TaskService):
    try:
        scheduler_task_id = callback.data.split(":")[2]
        # Удаляем задачу
        scheduler_task = task_service.scheduler_task_cache.pop(scheduler_task_id, None)

        if not scheduler_task:
            await callback.answer(
                "Задача не найдена",
                show_alert=True
            )
            return

        prew_text = "❌ <b>Вы удалили эту конфигурацию задачи по расписанию</b>\n\n"
        await callback.message.edit_text(
            text=prew_text + get_schedule_task_creation_message_by_state_schedule_task_obj(scheduler_task),
            reply_markup=None,
            parse_mode="HTML"
        )

        await callback.answer()

    except Exception:
        await callback.answer(
            "Ошибка",
            show_alert=True
        )

