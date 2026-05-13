from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery


class BanMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):

        user_service = data.get("user_service")
        if not user_service:
            return await handler(event, data)

        tg_user = getattr(event, "from_user", None)
        if not tg_user:
            return await handler(event, data)

        user = await user_service.register_in_cache(tg_user)
        if user.is_banned:
            if isinstance(event, Message):
                await event.answer("🚫 Вы заблокированы")
            elif isinstance(event, CallbackQuery):
                await event.answer("🚫 Вы заблокированы", show_alert=True)
            return  # ❌ стопаем pipeline

        return await handler(event, data)