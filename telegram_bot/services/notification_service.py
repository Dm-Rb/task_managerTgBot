from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup


class NotificationService:

    def __init__(self, bot: Bot):
        self.bot = bot


    async def send_to_user(self, user_id: int, text: str,
                           reply_markup: InlineKeyboardMarkup = None, parse_mode: str = "HTML"
                           ) -> bool:
        """Отправить сообщение пользователю"""

        try:
            await self.bot.send_message(chat_id=user_id, text=text, reply_markup=reply_markup, parse_mode=parse_mode)
            return True

        except Exception as e:
            print(f"[NotificationService] send_to_user error: {e}")
            return False

    async def send_to_group(self, group_id: int, text: str,
                            reply_markup: InlineKeyboardMarkup = None, parse_mode: str = "HTML") -> bool:
        """
        Отправить сообщение в группу
        """

        try:
            await self.bot.send_message(
                chat_id=group_id,
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )

            return True

        except Exception as e:
            print(f"[NotificationService] send_to_group error: {e}")
            return False

    async def broadcast_to_users(self,
        user_ids: list[int],
        text: str,
        reply_markup: InlineKeyboardMarkup = None,
        parse_mode: str = "HTML"
    ):
        """
        Массовая рассылка пользователям
        """

        for user_id in user_ids:
            await self.send_to_user(
                user_id=user_id,
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )