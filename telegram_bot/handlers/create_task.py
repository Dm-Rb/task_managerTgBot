from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from telegram_bot.states import CreateTaskStates  # FSM
from telegram_bot.services.user_service import UserService
from telegram_bot.services.task_service import TaskService
from telegram_bot.flows.create_task import show_templates_selection


router = Router(name="handlers_create_task")


@router.message(Command("create_task"))
async def create_task_start(message: Message, state: FSMContext, task_service: TaskService, user_service: UserService):
    """ Старт создания задачи """
    # очищаем состояние
    await state.clear()
    is_user_admin = await user_service.is_user_admin(message.from_user.id)
    if not is_user_admin:
        return await message.answer('У вас не достаточно прав для создания задач')

    # Делегируем отображение в flow
    await show_templates_selection(message, state, task_service)
    await state.set_state(CreateTaskStates.choosing_template)


@router.message(CreateTaskStates.waiting_template_title)
async def template_title_handler(message: Message, state: FSMContext):

    # записываем в фсм титульник нового шаблона
    await state.update_data(template_title=message.text)
    # меняем состояние
    await state.set_state(CreateTaskStates.waiting_template_description)

    await message.answer("Введите описание задачи 👇🏻")


@router.message(CreateTaskStates.waiting_template_description)
async def template_description_handler(message: Message, state: FSMContext, task_service):

    # достаём из фсм титульник нового шаблона
    data = await state.get_data()
    title = data["template_title"]

    # добавляем новый шаблон в
    description = message.text

    task_service.add_template(
        title=title,
        description=description
    )
    # Делегируем отображение в flow
    await show_templates_selection(message, state, task_service, "✅ Шаблон создан\n\n")
    await state.set_state(CreateTaskStates.choosing_template)


@router.message(CreateTaskStates.waiting_confirmation, F.text == "✅ Создать задачу")
async def confirm_create_task_handler(message: Message, state: FSMContext
):
    """Создание задачи"""
    # получаем все данные из FSM
    data = await state.get_data()
    print(data)
    # тут добавить передачу data в Task
    # очищаем состояние
    await state.clear()

    # удаляем Reply клавиатуру и отправляем сообщение об успехе
    # await message.answer(
    #     "✅ Задача успешно создана!",
    #     reply_markup=ReplyKeyboardRemove()
    # )

    # можно также удалить предыдущее сообщение с подтверждением
    # await message.delete()


@router.message(CreateTaskStates.waiting_confirmation, F.text == "❌ Отменить")
async def cancel_create_task_handler(
        message: Message,
        state: FSMContext
):
    """Отмена создания задачи"""
    # очищаем состояние
    await state.clear()

    # удаляем Reply клавиатуру
    # await message.answer(
    #     "❌ Создание задачи отменено",
    #     reply_markup=ReplyKeyboardRemove()
    # )

    # удаляем сообщение с кнопками (опционально)
    await message.delete()

    # также можно удалить предыдущие сообщения из истории
    # или отправить пользователя в начальное меню
