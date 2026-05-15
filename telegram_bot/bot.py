from core.config import settings
from telegram_bot.storage.user_cache import UserCache
from telegram_bot.storage.group_cache import GroupCache
from telegram_bot.storage.task_cache import TaskCache

from telegram_bot.services.user_service import UserService
from telegram_bot.services.group_service import GroupService
from telegram_bot.services.task_service import TaskService
from telegram_bot.services.notification_service import NotificationService
from telegram_bot.services.task_runtime_service import TaskRuntimeService

from telegram_bot.handlers.router import router as handlers_router
from telegram_bot.middlewares.ban_middleware import BanMiddleware
from telegram_bot.callbacks.create_task.router import router as callbacks_create_task
from telegram_bot.callbacks.update_task.router import router as callbacks_update_task


import asyncio
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher
from database.init_db import init_db
from database.repositories.user import UserRepository
from database.repositories.group import GroupRepository
from database.repositories.task import TaskRepository


from aiogram.types import BotCommand

async def set_main_menu(bot):
    main_menu_commands = [
        BotCommand(command='start', description='Запустить бота'),
        BotCommand(command='menu', description='Открыть меню'),
        BotCommand(command='show_tasks', description='Мои задачи'),
    ]

    await bot.set_my_commands(main_menu_commands)

async def start_bot():
    await init_db()  # Base.metadata.create_all создаём таблицы если их нет. Важно сделать на старте, а не ниже

    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # объекты для crud операций с базой данных
    user_database = UserRepository()
    group_database = GroupRepository()
    task_database = TaskRepository()
    # объекты для операций с самописным кешем
    user_cache = UserCache()
    group_cache = GroupCache()
    task_cache = TaskCache()
    # бизнес логика, объединяющая чтение\запись в самописный кеш и базу данных
    user_service = UserService(user_cache, user_database)
    group_service = GroupService(group_cache, group_database)
    task_service = TaskService(task_cache, None)
    notification_service = NotificationService(bot)
    runtime_service = TaskRuntimeService(task_service, notification_service)


    # регистрируем объекты в диспетчере что бы вызывать объекты прямо в хендлерах не ебаться с импортами
    dp["user_service"] = user_service
    dp["group_service"] = group_service
    dp["task_service"] = task_service
    dp["runtime_service"] = runtime_service


    # прогревваем кеш из базы данных
    await user_service.warm_up()
    await group_service.warm_up()

    dp.include_router(handlers_router)
    dp.include_router(callbacks_create_task)
    dp.include_router(callbacks_update_task)

    # мидлваре на бан
    dp.message.middleware(BanMiddleware())
    dp.callback_query.middleware(BanMiddleware())
    await set_main_menu(bot)
    try:
        await dp.start_polling(
            bot,
            # allowed_updates=dp.resolve_used_update_types()
        )
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(start_bot())