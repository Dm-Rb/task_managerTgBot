from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from telegram_bot.states import CompleteTaskStates, CompliteСashColletionStates
from telegram_bot.services.task_runtime_service import TaskRuntimeService
from telegram_bot.services.cash_collection_service import CashCollectionService
from telegram_bot.keyboards.cash_collection import confirm_keyboard
from telegram_bot.messages.cash_collection import show_complite_point

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


@router.message(CompliteСashColletionStates.waiting_comment, F.text)
async def cash_collection_task_comment_handler(message: Message, state: FSMContext, cash_collection_service: CashCollectionService):
    if message.text.startswith("/"):
        await message.answer('Отмена действия')
        return await state.clear()
    
    state_data = await state.get_data()
    task = cash_collection_service.tasks[state_data.get("parent_id")]
    point_id = state_data.get("point_id")
    for point in task.points:
        if point.id == point_id:
            point.comment = message.text
            return await message.answer(
                text=show_complite_point(point),
                reply_markup=confirm_keyboard('ask_complete_point', task.parent_id),
                parse_mode="HTML"
                )
    await state.clear()
    return await message.answer('Ошибка. Что то пошло не так')


