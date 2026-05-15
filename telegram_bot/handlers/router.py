"""Подключаем все модули пакета в единый роутер"""
from aiogram import Router

from telegram_bot.handlers import start_auth, logout, group_events, create_task, show_tasks, menu, media_handler, comment_comple_handler


router = Router()


router.include_router(group_events.router)
router.include_router(start_auth.router)
router.include_router(logout.router)
router.include_router(create_task.router)
router.include_router(show_tasks.router)
router.include_router(menu.router)
router.include_router(media_handler.router)
router.include_router(comment_comple_handler.router)