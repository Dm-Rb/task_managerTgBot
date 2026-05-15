from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from telegram_bot.states import CreateTaskStates
from telegram_bot.models.task import TaskTemplate
from telegram_bot.keyboards.create_task import task_templates_keyboard
from telegram_bot.flows.create_task import show_selected, show_templates_selection, show_address_selection, show_groups_selection


router = Router(name="task_template")


@router.callback_query(F.data.startswith("task_template:page:"))
async def template_page_handler(callback: CallbackQuery, task_service):
    """Пагинация списка шаблонов задач. Изменяет клавиатуру"""
    try:
        page = int(callback.data.split(":")[2])
    except (IndexError, ValueError):
        await callback.answer("Ошибка", show_alert=True)
        return

    task_templates: list[TaskTemplate] = task_service.get_all_task_templates()

    await callback.message.edit_reply_markup(
        reply_markup=task_templates_keyboard(task_templates=task_templates, page=page)
    )
    await callback.answer()


@router.callback_query(F.data == "task_template:create")
async def create_task_template(callback: CallbackQuery, state: FSMContext):
    """Создать шаблон"""
    # удаляем сообщение целиком
    await callback.message.delete()
    # переводим FSM
    await state.set_state(CreateTaskStates.waiting_template_title)
    # отправляем новое сообщение
    await callback.message.answer(
        "Введите название шаблона задачи 👇🏻"
    )

    await callback.answer()


@router.callback_query(F.data.startswith("task_template:select:"))
async def template_select_handler(callback: CallbackQuery, state: FSMContext, task_service):
    """Обработка выбора существующего шаблона (прессбатн)"""
    try:
        index = int(callback.data.split(":")[2])  # извлекаем индекс

    except (IndexError, ValueError):
        await callback.answer("Ошибка при выборе шаблона", show_alert=True)
        return

    task_templates: list[TaskTemplate] = task_service.get_all_task_templates()

    if index < 0 or index >= len(task_templates):
        await callback.answer("Шаблон не найден", show_alert=True)
        return

    task_template = task_templates[index]

    # cохраняем данные шаблона в FSM
    await state.update_data(
        template_title=task_template.title,
        template_description=task_template.description,
    )
    await show_selected(callback, state, 'task_template')  # делегируем отображение в flow
    await callback.answer()


@router.callback_query(F.data == "task_template:back")
async def template_back_handler(callback: CallbackQuery, state: FSMContext, task_service):
    """Вернуться на этап выбора шаблона"""

    await show_templates_selection(callback, state, task_service)
    await callback.answer()


#раскомментировать колбек адресов
@router.callback_query(F.data == "task_template:continue")
async def template_continue_handler(callback: CallbackQuery, state: FSMContext, task_service):
    """Перейти на этап выбора группы"""

    await show_address_selection(callback, state, task_service, '')
    await callback.answer()


# # удалить этот кусок
# @router.callback_query(F.data == "task_template:continue")
# async def template_continue_handler(callback: CallbackQuery, state: FSMContext, group_service):
#     """Перейти на этап выбора группы"""
#
#     await show_groups_selection(callback, state, group_service)
#     await callback.answer()