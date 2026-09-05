from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from telegram_bot.states import CreateTaskStates
from telegram_bot.models.task import TaskTemplate
from telegram_bot.services.template_service import TemplateService
from telegram_bot.keyboards.create_task import task_templates_keyboard, confirm_delete
from telegram_bot.flows.create_task import show_selected, show_tittles_selection, show_address_selection
from database.models.task_tittle import TaskTittleTemplateTable


router = Router()


@router.callback_query(F.data.startswith("task_template:page:"))
async def task_tiitles_paginatiom(callback: CallbackQuery, template_service: TemplateService):
    """Пагинация списка шаблонов задач. Изменяет клавиатуру"""
    try:
        page = int(callback.data.split(":")[2])
    except (IndexError, ValueError):
        await callback.answer("Ошибка", show_alert=True)
        return

    task_tittles: list[TaskTittleTemplateTable] = await template_service.get_all_task_tittles()

    await callback.message.edit_reply_markup(
        reply_markup=task_templates_keyboard(task_tittles=task_tittles, page=page)
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
async def template_select_handler(callback: CallbackQuery, state: FSMContext, template_service: TemplateService):
    """Обработка выбора существующего шаблона (прессбатн)"""
    try:
        task_tittle_id = int(callback.data.split(":")[2]) # извлекаем индекс
    except (IndexError, ValueError):
        await callback.answer("Ошибка при выборе шаблона", show_alert=True)
        return

    task_tittle = template_service.tittles[task_tittle_id]

    # cохраняем данные шаблона в FSM
    await state.update_data(
        template_title=task_tittle.tittle
    )
    await show_selected(callback, state, 'task_template', "🗑 Удалить этот шаблон задачи" if len(template_service.tittles.values()) > 0 else None)  # делегируем отображение в flow
    await callback.answer()


@router.callback_query(F.data == "task_template:back")
async def template_back_handler(callback: CallbackQuery, state: FSMContext, template_service: TemplateService):
    """Вернуться на этап выбора шаблона"""

    await show_tittles_selection(callback, state, template_service)
    await callback.answer()


@router.callback_query(F.data == "task_template:delete")
async def delete_tittle_question(callback: CallbackQuery):
    await callback.message.edit_text(text='Вы действительно хотите удалить этот объект?', reply_markup=confirm_delete("task_template"))
    await callback.answer()


@router.callback_query(F.data == "confirm_delete_no:task_template")
async def delete_tittle_answer_no(callback: CallbackQuery, state: FSMContext, template_service: TemplateService):
    await show_tittles_selection(callback, state, template_service)
    await callback.answer()


@router.callback_query(F.data == "confirm_delete_yes:task_template")
async def delete_tittle_answer_yes(callback: CallbackQuery, state: FSMContext, template_service: TemplateService):
    state_data = await state.get_data()
    if state_data.get('template_title', None):
        await template_service.remove_task_tittle_by_name(state_data['template_title'])
    await show_tittles_selection(callback, state, template_service)
    await state.clear()  # очищаем состояние
    await callback.answer()

#раскомментировать колбек адресов
@router.callback_query(F.data == "task_template:continue")
async def template_continue_handler(callback: CallbackQuery, state: FSMContext):
    """Перейти на этап ввода описания задачи"""
    # удаляем сообщение целиком
    await callback.message.delete()
    # переводим FSM
    await state.set_state(CreateTaskStates.waiting_template_description)
    # отправляем новое сообщение
    await callback.message.answer(
        "Введите описание для задачи 👇🏻"
    )
