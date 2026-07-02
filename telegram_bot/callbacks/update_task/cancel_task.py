from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from telegram_bot.services.user_service import UserService
from telegram_bot.services.task_runtime_service import TaskRuntimeService
from telegram_bot.services.task_service import TaskService

from telegram_bot.messages.task import get_task_message_by_task_obj
from telegram_bot.keyboards.update_task import performer_task_keyboard, confirm_keyboard


router = Router()


# @router.callback_query(F.data.startswith("task:cancel:"))
# async def accept_task_handler(callback: CallbackQuery, runtime_service: TaskRuntimeService):
#     try:
#         task_id = callback.data.split(":")[2]
#
#     except Exception:
#         await callback.answer(
#             "Ошибка",
#             show_alert=True
#         )
#         return
#
#     # Удаляем задачу
#
#     task = await runtime_service.cancel_task(task_id)
#
#     if not task:
#         await callback.answer(
#             "Задача не найдена",
#             show_alert=True
#         )
#         return
#
#     prew_text = "❌ <b>Вы отменили эту задачу</b>\n\n"
#     await callback.message.edit_text(
#         text=prew_text + get_task_message_by_task_obj(task),
#         reply_markup=performer_task_keyboard(task_id, task.status),
#         parse_mode="HTML"
#     )
#     await callback.answer()

@router.callback_query(F.data.startswith("task:cancel:"))
async def task_cancel_request(callback: CallbackQuery):
    task_id = callback.data.split(":")[2]

    if callback.message.text:
        await callback.message.edit_text(
            "Вы уверены, что хотите отменить задачу?",
            reply_markup=confirm_keyboard("task:cancel", task_id)
        )
    else:
        # если сообщение с документом — бот просто отправит новое сообщение с кнопками.
        await callback.message.answer(
            "Вы уверены, что хотите отменить задачу?",
            reply_markup=confirm_keyboard("task:cancel", task_id)
        )

    await callback.answer()