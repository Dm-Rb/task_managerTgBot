from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from telegram_bot.states import CompleteTaskStates
from telegram_bot.messages.task import get_task_message_by_task_obj
from telegram_bot.flows.update_task import show_message_attach_photo


router = Router()


@router.callback_query(F.data.startswith("task:complete:"))
async def complete_task_start(callback: CallbackQuery, state: FSMContext, task_service):

    task_id = callback.data.split(":")[2]

    await state.update_data(
        task_id=task_id,
        media=[],
        media_group_processed=False
    )
    task = task_service.get_task(task_id)
    message_text = get_task_message_by_task_obj(task)
    await show_message_attach_photo(callback, state, message_text)
    await callback.message.delete()

    # await callback.message.edit_text(
    #     text= "📸 Прикрепите фото или видео отчёт о проделанной работе.\n\n",
    #     keyword=None,
    #     parse_mode='HTML'
    # )

    # await state.set_state(CompleteTaskStates.waiting_media)

    await callback.answer()