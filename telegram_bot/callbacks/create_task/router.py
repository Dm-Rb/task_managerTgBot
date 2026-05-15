"""Подключаем все модули пакета в единый роутер"""
from aiogram import Router
from telegram_bot.callbacks.create_task.task_template import router as task_template_router
from telegram_bot.callbacks.create_task.groups import router as group_router
from telegram_bot.callbacks.create_task.performer import router as performer_router
from telegram_bot.callbacks.create_task.priority import router as priority_router
from telegram_bot.callbacks.create_task.task_type import router as task_type_router
from telegram_bot.callbacks.create_task.new_task import router as new_task_router
from telegram_bot.callbacks.create_task.task_recurrence import router as task_recurrence_router


router = Router(name="callbacks_create_task")


router.include_router(task_template_router)
router.include_router(group_router)
router.include_router(performer_router)
router.include_router(priority_router)
router.include_router(task_type_router)
router.include_router(task_recurrence_router)


router.include_router(new_task_router)


