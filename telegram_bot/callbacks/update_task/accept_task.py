from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from telegram_bot.services.user_service import UserService
from telegram_bot.services.task_runtime_service import TaskRuntimeService
from telegram_bot.messages.task import get_task_message_by_task_obj
from telegram_bot.keyboards.update_task import performer_task_keyboard


router = Router()

@router.callback_query(F.data.startswith("task:accept:"))
async def accept_task_handler(
    callback: CallbackQuery,
    runtime_service: TaskRuntimeService
):
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

    if not task:
        await callback.answer(
            "Задача не найдена",
            show_alert=True
        )
        return

    prew_text = "🆙 <b>Вы в процессе выполнения данной задачи</b>\n\n"
    await callback.message.edit_text(
        text=prew_text + get_task_message_by_task_obj(task),
        reply_markup=performer_task_keyboard(task_id, task.status),
        parse_mode="HTML"
    )

    await callback.answer(
        "✅ Задача принята в работу"
    )
