from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from telegram_bot.flows.create_task import (
    show_selected,
    show_address_selection,
    show_groups_selection
)

from telegram_bot.models.task import AddressTemplate
from telegram_bot.states import CreateTaskStates

router = Router(name="address")


@router.callback_query(F.data.startswith("address:page:"))
async def address_page_handler(
    callback: CallbackQuery,
    task_service
):
    try:
        page = int(callback.data.split(":")[2])

    except:
        await callback.answer("Ошибка", show_alert=True)
        return

    templates = task_service.get_all_address_templates()

    from telegram_bot.keyboards.create_task import address_templates_keyboard

    await callback.message.edit_reply_markup(
        reply_markup=address_templates_keyboard(
            templates,
            page=page
        )
    )

    await callback.answer()


@router.callback_query(F.data.startswith("address:page:"))
async def address_page_handler(
    callback: CallbackQuery,
    task_service
):
    try:
        page = int(callback.data.split(":")[2])

    except:
        await callback.answer("Ошибка", show_alert=True)
        return

    templates = task_service.get_all_address_templates()

    from telegram_bot.keyboards.create_task import address_templates_keyboard

    await callback.message.edit_reply_markup(
        reply_markup=address_templates_keyboard(
            templates,
            page=page
        )
    )

    await callback.answer()

@router.callback_query(F.data.startswith("address:select:"))
async def address_select_handler(
    callback: CallbackQuery,
    state: FSMContext,
    task_service
):
    try:
        index = int(callback.data.split(":")[2])

    except:
        await callback.answer("Ошибка", show_alert=True)
        return

    templates = task_service.get_all_address_templates()

    if index >= len(templates):
        await callback.answer("Адрес не найден", show_alert=True)
        return

    template = templates[index]

    await state.update_data(
        address=template.address
    )

    await show_selected(
        callback,
        state,
        "address"
    )

    await callback.answer()

@router.callback_query(F.data == "address:none")
async def address_none_handler(
    callback: CallbackQuery,
    state: FSMContext
):

    await state.update_data(
        address=None
    )

    await show_selected(
        callback,
        state,
        "address"
    )

    await callback.answer()

@router.callback_query(F.data == "address:create")
async def create_address_template(
    callback: CallbackQuery,
    state: FSMContext
):

    await callback.message.delete()

    await state.set_state(
        CreateTaskStates.waiting_address_template
    )

    await callback.message.answer(
        "Введите адрес шаблона"
    )

    await callback.answer()


@router.callback_query(F.data == "address:continue")
async def address_continue_handler(
    callback: CallbackQuery,
    state: FSMContext,
    group_service
):

    await show_groups_selection(
        callback,
        state,
        group_service
    )

    await callback.answer()