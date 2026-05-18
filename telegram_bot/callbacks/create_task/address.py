from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from telegram_bot.keyboards.create_task import address_templates_keyboard
from telegram_bot.flows.create_task import show_selected, show_address_selection, show_templates_selection, show_groups_selection
from telegram_bot.states import CreateTaskStates
from telegram_bot.storage.task_cache import AddressTemplate
from telegram_bot.services.task_service import TaskService
from telegram_bot.services.group_service import GroupService


router = Router()


@router.callback_query(F.data.startswith("address:page:"))
async def address_page_handler(callback: CallbackQuery, task_service: TaskService):
    """Пагинация шаблонов с адресами"""
    try:
        page = int(callback.data.split(":")[2])
    except:
        await callback.answer("Ошибка", show_alert=True)
        return

    templates: list[AddressTemplate] = task_service.get_all_address_templates()

    await callback.message.edit_reply_markup(
        reply_markup=address_templates_keyboard(templates, page=page
        )
    )

    await callback.answer()


@router.callback_query(F.data == "address:create")
async def create_task_template(callback: CallbackQuery, state: FSMContext):
    """Создать шаблон"""
    # удаляем сообщение целиком
    await callback.message.delete()
    # переводим FSM
    await state.set_state(CreateTaskStates.waiting_address_template)
    # отправляем новое сообщение
    text = "Введите адрес для задачи 👇🏻"
    await callback.message.answer(text)

    await callback.answer()


@router.callback_query(F.data.startswith("address:select:"))
async def address_select_handler(callback: CallbackQuery, state: FSMContext, task_service: TaskService):
    """Обработка нажатия на кнопку адреса"""
    try:
        index = int(callback.data.split(":")[2])

    except:
        await callback.answer("Ошибка", show_alert=True)
        return

    templates: list[AddressTemplate] = task_service.get_all_address_templates()

    if index >= len(templates):
        await callback.answer("Ошибка", show_alert=True)
        return
    template: AddressTemplate = templates[index]
    await state.update_data(address=template.address)

    await show_selected(callback, state, "address", True if len(templates) > 0 else None)
    await callback.answer()


@router.callback_query(F.data == "address:none")
async def address_none_handler(callback: CallbackQuery, state: FSMContext):
    """Обработка нажатия на кнопку Без адреса"""
    await state.update_data(address=None)
    await show_selected(callback, state, "address")
    await callback.answer()


@router.callback_query(F.data == "address:back")
async def address_continue_handler(callback: CallbackQuery, state: FSMContext, task_service: TaskService):
    """Вернуться на этап выбора шаблона задачи"""
    await show_address_selection(callback, state, task_service)
    await callback.answer()


@router.callback_query(F.data == "address:delete")
async def create_task_template(callback: CallbackQuery, state: FSMContext, task_service: TaskService):
    state_data = await state.get_data()
    if state_data.get('address', None):
        task_service.remove_address_template(state_data['address'])
    await show_address_selection(callback, state, task_service)
    await callback.answer()


@router.callback_query(F.data == "address:continue")
async def address_continue_handler(callback: CallbackQuery, state: FSMContext, group_service: GroupService):
    """Перейти на следующий этап выбора адреса"""
    await show_groups_selection(callback, state, group_service)
    await callback.answer()