from core.config import settings
from core.app_context import AppContext

from telegram_bot.handlers.router import router as handlers_router
from telegram_bot.middlewares.ban_middleware import BanMiddleware
from telegram_bot.callbacks.create_task.router import router as callbacks_create_task
from telegram_bot.callbacks.update_task.router import router as callbacks_update_task
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand


async def set_main_menu(bot):
    main_menu_commands = [
        BotCommand(command='start', description='Запустить бота'),
        BotCommand(command='menu', description='Открыть меню'),
        BotCommand(command='show_tasks', description='Мои задачи'),
    ]

    await bot.set_my_commands(main_menu_commands)


async def create_bot():

    bot = Bot(token=settings.BOT_TOKEN)

    dp = Dispatcher(
        storage=MemoryStorage()
    )
    context = AppContext(bot)

    await context.warm_up()

    # Передаём сервисы в aiogram
    dp["user_service"] = context.user_service
    dp["group_service"] = context.group_service
    dp["task_service"] = context.task_service
    dp["template_service"] = context.template_service
    dp["runtime_service"] = context.runtime_service

    dp.include_router(handlers_router)
    dp.include_router(callbacks_create_task)
    dp.include_router(callbacks_update_task)

    dp.message.middleware(BanMiddleware())
    dp.callback_query.middleware(BanMiddleware())

    await set_main_menu(bot)

    return bot, dp, context