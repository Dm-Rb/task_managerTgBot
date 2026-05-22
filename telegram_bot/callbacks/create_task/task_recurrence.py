# from aiogram import Router, F
# from aiogram.types import CallbackQuery
# from aiogram.fsm.context import FSMContext
# from telegram_bot.flows.create_task import show_schedule_task_confirmation, show_recurrence_task_repeat
# from telegram_bot.states import CreateTaskStates
#
#
# router = Router(name="task_recurrence")
#
#
# @router.callback_query(F.data.startswith("recurrence_task:repeat:"))
# async def recurrence_task_repeat_handler(callback: CallbackQuery, state: FSMContext):
#     try:
#         every_n = callback.data.split(":")[2] # '1' or 'set'
#     except:
#         await callback.answer("Ошибка при выборе исполнителя", show_alert=True)
#         return
#
#     if every_n == 'set':
#         # меняем состояние, удаляем сообщение. срабатывает хендлер на сосотояние который просит пользователя ввести данные
#         await show_recurrence_task_repeat(callback, state)
#     elif every_n == "1":
#         await state.update_data(every_n_days=1)
#         await show_schedule_task_confirmation(callback, state)
