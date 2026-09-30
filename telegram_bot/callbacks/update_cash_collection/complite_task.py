from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from telegram_bot.services.cash_collection_service import CashCollectionService
from telegram_bot.services.cash_collection_runtime_service import CashCollectionRuntimeService
from telegram_bot.messages.cash_collection import start_point
from telegram_bot.keyboards.cash_collection import show_points_for_perfomer
from telegram_bot.states import CompliteСashColletionStates
from telegram_bot.messages.cash_collection import remaining_points_for_perfomer

import datetime

router = Router()
@router.callback_query(F.data.startswith("comptile_cc_task:page:"))
async def cash_collection_choise_point_pagination(callback: CallbackQuery, cash_collection_service: CashCollectionService):
    """Пагинация точек для исполнителя"""
    try:
        _, _, parent_id, page_str = callback.data.split(":")
        page = int(page_str)
    except (ValueError, IndexError):
        await callback.answer("Ошибка", show_alert=True)
        return

    task = cash_collection_service.tasks.get(parent_id)
    if task is None:
        await callback.answer("Задача не найдена", show_alert=True)
        return

    await callback.message.edit_reply_markup(
        reply_markup=show_points_for_perfomer(task, page=page)
    )

    await callback.answer()
  
@router.callback_query(F.data.startswith("comptile_cc_task:select:"))
async def cash_collection_choised_point(callback: CallbackQuery, state: FSMContext, cash_collection_service: CashCollectionService):
    """Выбор конкретной точки исполнителем"""
    try:
        _, _, parent_id, point_id = callback.data.split(":")
    except ValueError:
        await callback.answer("Ошибка", show_alert=True)
        return
    task = cash_collection_service.tasks[parent_id]
    point = None
    for p in task.points:
        if p.id == point_id:
            point = p
            break
    if point is None:
        return await callback.answer("Ошибка", show_alert=True)
    message = start_point(point)
    await callback.message.edit_text(
        text=message,
        reply_markup=None,
        parse_mode="HTML"
    )
    await state.update_data(parent_id=parent_id, point_id=point.id)
    await state.set_state(CompliteСashColletionStates.waiting_photo_before_collection)
    await callback.answer()

@router.callback_query(F.data.startswith("ask_complete_point"))
async def ask_complete_point(callback: CallbackQuery, 
                             cash_collection_service: CashCollectionService,
                             cash_collection_runtime_service: CashCollectionRuntimeService,
                             state: FSMContext):
    action, task_id, answer = callback.data.split(":")
    if answer == "yes":
        state_data = await state.get_data()
        task = cash_collection_service.tasks[state_data.get("parent_id")]
        point_id = state_data.get("point_id")
        for point in task.points:
            if point.id == point_id:
                point.status = "Выполнена"
                point.completed_at = datetime.datetime.now()
                point.is_active = False
                await cash_collection_service.sync_point(task, point)
                # уведомить создателя 
                await cash_collection_runtime_service.сompleted_point_for_creator(task, point)
                break
        in_porocess_points = [p for p in task.points if p.status == "В процессе"]
        if in_porocess_points:
            message = remaining_points_for_perfomer(in_porocess_points)     
        else:
            message = f"<b>✅ Все пункты в городе {task.city} проинкассированы!</b>"
            # удаляем из кеша задачу
            del cash_collection_service.tasks[state_data['parent_id']]
            
        await callback.message.edit_text(text=message, reply_markup=None, parse_mode="HTML")
        
    elif answer == "no":
         await callback.message.delete()        
    return await state.clear()
    