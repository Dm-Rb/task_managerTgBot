"""Подключаем все модули пакета в единый роутер"""
from aiogram import Router
from telegram_bot.callbacks.update_task.accept_task import router as accept_task_router
from telegram_bot.callbacks.update_task.cancel_task import router as cancel_task_router


router = Router()


router.include_router(accept_task_router)
router.include_router(cancel_task_router)



