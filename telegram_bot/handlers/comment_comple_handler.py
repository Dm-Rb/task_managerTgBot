from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from telegram_bot.states import CompleteTaskStates
from telegram_bot.services.task_runtime_service import TaskRuntimeService


router = Router()


@router.message(CompleteTaskStates.waiting_comment, F.text)
async def complete_task_comment_handler(message: Message, state: FSMContext, runtime_service: TaskRuntimeService):

    data = await state.get_data()
    task_id = data["task_id"]
    media: list = data["media"]
    comment: str = message.text

    await runtime_service.complete_task(
        task_id=task_id,
        media=media,
        comment=comment
    )

    await state.clear()