"""Подключаем все модули пакета в единый роутер"""
from aiogram import Router
from telegram_bot.callbacks.create_cash_collection.city import router as city_router
from telegram_bot.callbacks.create_cash_collection.submenu import router as submenu_router
from telegram_bot.callbacks.create_cash_collection.perfomer import router as perfomer_router
from telegram_bot.callbacks.create_cash_collection.description import router as description_router


router = Router()


router.include_router(city_router)
router.include_router(submenu_router)
router.include_router(perfomer_router)
router.include_router(description_router)
