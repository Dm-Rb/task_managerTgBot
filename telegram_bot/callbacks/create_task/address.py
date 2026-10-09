from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from telegram_bot.keyboards.create_task import city_address_keyboard, confirm_delete
from telegram_bot.flows.create_task import show_selected, show_city_selection, show_address_selection, show_groups_selection
from telegram_bot.states import CreateTaskStates
from telegram_bot.storage.task_cache import AddressTemplate
from telegram_bot.services.template_service import TemplateService
from telegram_bot.services.group_service import GroupService


router = Router()


@router.callback_query(F.data.startswith(("city:page:", "address:page:")))
async def address_page_handler(callback: CallbackQuery, template_service: TemplateService):
    """Пагинация шаблонов с адресами"""
    try:
        page = int(callback.data.split(":")[2])
    except:
        await callback.answer("Ошибка", show_alert=True)
        return
    
    if F.data.startswith("city:page:"):
        await callback.message.edit_reply_markup(
            reply_markup=city_address_keyboard(template_service.cities, "city", page=page
            )
        )
    elif  F.data.startswith("address:page:"):
        await callback.message.edit_reply_markup(
            reply_markup=city_address_keyboard(template_service.adreses, "adress", page=page
            )
        )
    else:
        await callback.answer("Ошибка", show_alert=True) 
    await callback.answer()


@router.callback_query(F.data.startswith(("city:select:", "address:select:")))
async def address_select_handler(callback: CallbackQuery, state: FSMContext, template_service: TemplateService):
    """Обработка нажатия на кнопку адреса"""
    try:
        key_ = int(callback.data.split(":")[2])

    except:
        await callback.answer("Ошибка", show_alert=True)
        return
    if callback.data.startswith("city:select:"):
        await state.update_data(city_id=key_, address=f"{template_service.cities[key_].city}")
        await show_selected(callback, state, "city")

    elif callback.data.startswith("address:select:"):
        data = await state.get_data()
        city_id = data.get("city_id")
        await state.update_data(
            address=f"{template_service.cities[city_id].city}, {template_service.adreses[key_].adress}"
        )
        await show_selected(callback, state, "address")

    await callback.answer()


@router.callback_query(F.data == "city:none")
async def address_none_handler(callback: CallbackQuery, state: FSMContext, group_service: GroupService):
    """Обработка нажатия на кнопку Без адреса"""
    await state.update_data(address=None)
    await address_continue_handler(callback, state, group_service)


@router.callback_query(F.data == "city:back")
async def address_back_handler(callback: CallbackQuery, state: FSMContext, template_service: TemplateService):
    """Вернуться на этап выбора города"""
    await show_city_selection(callback, state, template_service)
    await callback.answer()


@router.callback_query(F.data == "city:continue")
async def city_continue_handler(callback: CallbackQuery, state: FSMContext, template_service: TemplateService):
    """Перейти на этап выбора адреса"""
    await show_address_selection(callback, state, template_service)
    await callback.answer()

@router.callback_query(F.data == "address:continue")
async def address_continue_handler(callback: CallbackQuery, state: FSMContext, group_service: GroupService):
    """Перейти на этап выбора группы"""
    await show_groups_selection(callback, state, group_service)
    await callback.answer()
