from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from telegram_bot.services.cash_collection_service import CashCollectionService
from telegram_bot.services.cash_collection_runtime_service import CashCollectionRuntimeService

from telegram_bot.messages.cash_collection import remove_tasks_for_perfomer
from telegram_bot.keyboards.cash_collection import confirm_keyboard

router = Router()


@router.callback_query(F.data.startswith("cash_collection_task:ask_cnf_rm:"))
async def cancel_new_scheduler_task_handler(callback: CallbackQuery):
    parent_id = callback.data.split(":")[2]
    await callback.message.edit_text(
        text="<b>Вы уверены, что хотите снять текущие задачи по инкассации?</b>",
        reply_markup=confirm_keyboard("confirm_cash_cllton_tsk", parent_id), 
        parse_mode="HTML"
    )
    
@router.callback_query(F.data.startswith("confirm_cash_cllton_tsk"))
async def confirm_remove_yes(callback: CallbackQuery, 
                             cash_collection_service: CashCollectionService,
                             cash_collection_runtime_service: CashCollectionRuntimeService,
                             state: FSMContext):
    action, parent_id, answer = callback.data.split(":")
    if answer == "yes":
        task = cash_collection_service.tasks.get(parent_id)
        if not task:
            raise ValueError(f"task with parent_id == {parent_id} not found in <cash_collection_service.tasks>")
        message = remove_tasks_for_perfomer(task)
        await cash_collection_runtime_service.send_message_to_user(task.performer_id, message)
        task = cash_collection_service.tasks[parent_id]
        await cash_collection_service.remove_task(parent_id)
        await callback.message.edit_text(
        text=f"Список задач по инкассации в городе <b>{task.city}</b> был удалён",
        reply_markup=None, 
        parse_mode="HTML"
            )
        
    elif answer == "no":
         await callback.message.delete()        
    await state.clear()
    return


@router.callback_query(F.data.startswith("cash_collection:task_list"))
async def show_task_collection_active_tasks(callback: CallbackQuery, cash_collection_runtime_service: CashCollectionRuntimeService):
    """Отработка кнопки Список активных задач"""
    await cash_collection_runtime_service.get_all_tasks_for_creator(callback.from_user.id)    
    await callback.answer()
