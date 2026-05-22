from telegram_bot.messages.task import get_schedule_task_creation_message_by_state_schedule_task_obj
from aiogram import Router, F
from aiogram.types import CallbackQuery

from telegram_bot.services.task_runtime_service import TaskRuntimeService
from telegram_bot.services.task_service import TaskService

from telegram_bot.messages.task import get_task_message_by_task_obj
from telegram_bot.keyboards.update_task import performer_task_keyboard, confirm_keyboard


router = Router()


@router.callback_query(F.data.startswith("confirm:"))
async def confirm_handler(callback: CallbackQuery, runtime_service, task_service):
    try:
        parts = callback.data.split(":")

        decision = parts[-1]              # yes / no
        object_id = parts[-2]             # id
        action = ":".join(parts[1:-2])    # task:cancel или scheduler_task:cancel

        if decision == "no":
            await callback.message.edit_text("❌ Отменена отменены")
            await callback.answer()
            return

        # TASK
        if action == "task:cancel":

            task = await runtime_service.cancel_task(object_id)

            if not task:
                await callback.answer(
                    "Задача не найдена",
                    show_alert=True
                )
                return

            prew_text = "❌ <b>Вы отменили эту задачу</b>\n\n"
            await callback.message.edit_text(
                text=prew_text + get_task_message_by_task_obj(task),
                reply_markup=performer_task_keyboard(object_id, task.status),
                parse_mode="HTML"
            )
            await callback.answer()

        # SCHEDULER
        elif action == "scheduler_task:cancel":
            scheduler_task = task_service.scheduler_task_cache.pop(object_id, None)
            prew_text = "❌ <b>Вы удалили эту конфигурацию задачи по расписанию</b>\n\n"
            await callback.message.edit_text(
                text=prew_text + get_schedule_task_creation_message_by_state_schedule_task_obj(scheduler_task),
                reply_markup=None,
                parse_mode="HTML"
            )

            await callback.answer()



        await callback.answer()

    except Exception as e:
        await callback.answer(f"Ошибка: {e}", show_alert=True)