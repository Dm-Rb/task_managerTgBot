import asyncio
import uvicorn
from database.init_db import init_db
from telegram_bot.bot import create_bot
from web_app.app import create_app
from core.config import settings


async def run_fastapi(app):

    config = uvicorn.Config(
        app,
        host=settings.HOST,
        port=settings.PORT,
        loop="asyncio",
    )

    server = uvicorn.Server(config)

    await server.serve()


async def run():

    # Создаём таблицы
    await init_db()

    # Создаём Telegram + общие сервисы
    bot, dp, context = await create_bot()

    # # Создаём FastAPI на том же context
    app = create_app(context)

    # Запускаем scheduler
    scheduler_task = asyncio.create_task(
        context.scheduler_service.start()
    )

    try:

        await asyncio.gather(
            dp.start_polling(bot),
            run_fastapi(app),
        )

    finally:

        scheduler_task.cancel()

        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(run())
