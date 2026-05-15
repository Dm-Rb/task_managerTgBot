from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from telegram_bot.states import CompleteTaskStates
from telegram_bot.services.task_runtime_service import TaskRuntimeService
import asyncio


router = Router()


@router.message(CompleteTaskStates.waiting_media, F.media_group_id)
async def complete_task_media_group_handler(message: Message, state: FSMContext, runtime_service):
    """Хендлер для отлова медиагруппы в моменте закрытия задачи"""
    data = await state.get_data()
    media = data.get("media", [])

    if message.photo:
        media.append({
            "type": "photo",
            "file_id": message.photo[-1].file_id
        })

    elif message.video:
        media.append({
            "type": "video",
            "file_id": message.video.file_id
        })

    # сохраняем промежуточно
    await state.update_data(media=media)
    # ожидаем обновлений
    await asyncio.sleep(0.1)

    # проверить флаг процесса. в колбеке при нажатии на кнопку Завершить задачу в state задаётся флаг media_group_processed=False

    data = await state.get_data()

    if data.get("media_group_processed"):
        return

    await state.update_data(media_group_processed=True)

    if message.caption:
        data = await state.get_data()
        media = data.get("media", [])

        await runtime_service.complete_task(
            task_id=data["task_id"],
            media=media,
            comment=message.caption
        )

        await state.clear()
        return

    await message.answer(
        "✍️ Добавьте текстовый комментарий "
        "к отчёту о проделанной работе."
    )

    await state.set_state(CompleteTaskStates.waiting_comment)


@router.message(CompleteTaskStates.waiting_media, F.photo | F.video)
async def complete_task_media_handler(message: Message, state: FSMContext, runtime_service: TaskRuntimeService):
    """Хендлер для отлова одиночной загруки фото или видео в моменте закрытия задачи"""

    media_data = []
    if message.photo:

        media_data.append({
            "type": "photo",
            "file_id": message.photo[-1].file_id
        })
    elif message.video:

        media_data.append({
            "type": "video",
            "file_id": message.video.file_id
        })

    # сохраняем список словарей в фсм
    await state.update_data(
        media=media_data
    )

    # если пользователь снабдил дополнительно текстом фото\видеоотчёт - вызываем метол runtime_service.complete_task
    if message.caption:
        data = await state.get_data()
        await runtime_service.complete_task(
            task_id=data["task_id"],
            media=media_data,
            comment=message.caption
        )
        await state.clear()
        return

    # если текста нет - просим пользователя отправить сопроводительный текст и меняем состояние. далее оно отлавливается
    # хендлером из модуля complete_task_comment_handler
    await message.answer(
        "✍️ Добавьте текстовый комментарий "
        "к отчёту о проделанной работе."
    )

    await state.set_state(
        CompleteTaskStates.waiting_comment
    )