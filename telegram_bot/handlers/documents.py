import asyncio
import io
import zipfile
from collections import defaultdict
from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, BufferedInputFile
from telegram_bot.flows.create_task import show_task_confirmation
from telegram_bot.states import CreateTaskStates


router = Router()



"""если после последнего сообщения группы прошло время этой константы
считаем, что вся media group получена."""

MEDIA_GROUP_DEBOUNCE = 0.5

"""
Хранилище активных collector-задач

key:
    (chat_id, media_group_id)

value:
    asyncio.Task

Почему chat_id тоже входит в key:
media_group_id уникален в контексте чата, поэтому так
мы дополнительно исключаем возможные пересечения.
"""

document_group_tasks: dict[tuple[int, str], asyncio.Task] = {}


async def remove_upload_keyboard(message: Message, state: FSMContext) -> None:
    """
    Удаляет inline-клавиатуру у сообщения,
    которое было показано пользователю перед загрузкой файлов.
    """

    data = await state.get_data()
    upload_message_id = data.get("upload_message_id")

    if not upload_message_id:
        return

    try:
        await message.bot.edit_message_reply_markup(
            chat_id=message.chat.id,
            message_id=upload_message_id,
            reply_markup=None,
        )
    except TelegramBadRequest:
        pass


def make_unique_filename(filename: str, used_names: set[str],index: int) -> str:
    """
    Делает имя файла уникальным внутри ZIP.
    """

    if filename not in used_names:
        used_names.add(filename)
        return filename

    name_parts = filename.rsplit(".", 1)

    if len(name_parts) == 2:
        name, extension = name_parts
        unique_name = f"{name}_{index}.{extension}"
    else:
        unique_name = f"{filename}_{index}"

    # На всякий случай проверяем и это имя.
    counter = 2
    original_unique_name = unique_name

    while unique_name in used_names:
        name_parts = original_unique_name.rsplit(".", 1)

        if len(name_parts) == 2:
            name, extension = name_parts
            unique_name = (
                f"{name}_{counter}.{extension}"
            )
        else:
            unique_name = (
                f"{original_unique_name}_{counter}"
            )

        counter += 1

    used_names.add(unique_name)

    return unique_name


async def add_document_to_group(message: Message, state: FSMContext) -> None:
    """
    Сохраняет информацию о документе медиагруппы в FSM.
    Сам файл здесь не скачивается.
    """

    data = await state.get_data()

    documents = data.get("documents", [])

    documents.append(
        {
            "file_id": message.document.file_id,
            "file_name": (
                message.document.file_name
                or f"document_{len(documents) + 1}"
            ),
        }
    )

    await state.update_data(
        documents=documents,
    )


async def create_documents_zip(message: Message,documents: list[dict]) -> bytes:
    """
    Скачивает документы из Telegram в оперативную память
    и создаёт ZIP в оперативной памяти.
    """

    zip_buffer = io.BytesIO()

    used_names: set[str] = set()

    with zipfile.ZipFile(
        zip_buffer,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
    ) as zip_file:

        for index, document in enumerate(
            documents,
            start=1,
        ):
            file_id = document["file_id"]
            original_filename = document["file_name"]

            # Делаем имя уникальным
            filename = make_unique_filename(
                filename=original_filename,
                used_names=used_names,
                index=index,
            )

            # Получаем информацию о файле Telegram
            telegram_file = await message.bot.get_file(
                file_id=file_id,
            )
            # Скачиваем файл в RAM
            file_buffer = io.BytesIO()

            await message.bot.download_file(
                telegram_file.file_path,
                destination=file_buffer,
            )

            file_buffer.seek(0)
            # Добавляем файл в ZIP
            zip_file.writestr(
                filename,
                file_buffer.read(),
            )

            file_buffer.close()

    zip_buffer.seek(0)
    zip_data = zip_buffer.read()
    zip_buffer.close()

    return zip_data


async def process_document_group(
    message: Message,
    state: FSMContext,
    task_key: tuple[int, str],
) -> None:
    """
    Ждёт debounce-интервал.
    Если за это время пришёл новый документ той же группы,
    предыдущая задача будет отменена.
    Если новых документов нет — создаём ZIP.
    """

    try:
        # Debounce
        await asyncio.sleep(
            MEDIA_GROUP_DEBOUNCE
        )

        data = await state.get_data()
        documents = data.get(
            "documents",
            [],
        )

        if not documents:
            return
        # Создаём ZIP
        zip_data = await create_documents_zip(
            message=message,
            documents=documents,
        )
        # Подготавливаем файл для Telegram
        zip_file = BufferedInputFile(
            file=zip_data,
            filename="documents.zip",
        )
        # Отправляем ZIP пользователю
        sent_message = await message.answer_document(
            document=zip_file,
            caption="Файлы заархивированы 🗂"
        )
        # Получаем file_id отправленного ZIP
        zip_file_id = sent_message.document.file_id
        # Сохраняем ZIP в том же поле

        await state.update_data(
            file_id=zip_file_id,
            documents=[],
        )
        await show_task_confirmation(sent_message, state)

    except asyncio.CancelledError:
        # Это нормальная ситуация.
        # Новый документ той же группы пришёл раньше,
        # чем закончился debounce.
        # Старый timer отменяется.
        raise

    except Exception:
        raise

    finally:
        # Удаляем task из глобального словаря,
        # но только если это всё ещё наша задача.

        current_task = document_group_tasks.get(
            task_key
        )

        if current_task is asyncio.current_task():
            document_group_tasks.pop(
                task_key,
                None,
            )

@router.message(CreateTaskStates.waiting_files, F.document)
async def document_handler(message: Message, state: FSMContext):
    """
    Обрабатывает как одиночные документы,
    так и media group из нескольких документов.

    Один документ:
        state["file_id"] = original_file_id

    Несколько документов:
        документы -> ZIP -> state["file_id"] = zip_file_id
    """

    # Удаляем клавиатуру сообщения с инструкцией
    await remove_upload_keyboard(
        message,
        state,
    )

    # Одиночный док
    if not message.media_group_id:

        await state.update_data(
            file_id=message.document.file_id,
        )

        await show_task_confirmation(
            message,
            state,
        )

        return
    
    # Медиагруппа
    media_group_id = message.media_group_id

    task_key = (
        message.chat.id,
        media_group_id,
    )

    # Добавляем документ в накопитель
    await add_document_to_group(
        message,
        state,
    )

    # Проверяем, есть ли уже timer для этой группы
    old_task = document_group_tasks.get(
        task_key
    )

    if old_task and not old_task.done():
        # Новый документ пришёл раньше окончания
        # предыдущего debounce.
        # Отменяем старый timer.
        old_task.cancel()

    # Запускаем новый timer
    new_task = asyncio.create_task(
        process_document_group(
            message=message,
            state=state,
            task_key=task_key,
        )
    )

    document_group_tasks[task_key] = new_task
    