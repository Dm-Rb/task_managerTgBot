from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from telegram_bot.states import CompleteTaskStates


router = Router()


@router.callback_query(F.data.startswith("task:complete:"))
async def complete_task_start(callback: CallbackQuery, state: FSMContext):

    task_id = callback.data.split(":")[2]

    await state.update_data(
        task_id=task_id,
        media=[],
        media_group_processed=False
    )

    await callback.message.edit_text(
        text= "📸 Прикрепите фото или видео отчёт о проделанной работе.\n\n",
        keyword=None,
        parse_mode='HTML'
    )

    await state.set_state(CompleteTaskStates.waiting_media)

    await callback.answer()