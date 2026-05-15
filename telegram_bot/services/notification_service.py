from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup
from aiogram.types import (InputMediaPhoto, InputMediaVideo)


class NotificationService:

    def __init__(self, bot: Bot):
        self.bot = bot

    async def send_to_user(self, user_id: int, text: str, reply_markup: InlineKeyboardMarkup = None,
                           parse_mode: str = "HTML") -> bool:
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

    async def send_photo_to_user(self, user_id: int, photo_id: str, text: str):
        """Отпраляет пользователю фото (уже загруженнов в тг) и текст"""
        await self.bot.send_photo(
            chat_id=user_id,
            photo=photo_id,
            caption=text,
            parse_mode="HTML"
        )

    async def send_photo_to_group(self, group_id: int, photo_id: str, text: str, thread_id: int or None = None):
        """Отпраляет в группу фото (уже загруженнов в тг) и текст"""

        await self.bot.send_photo(
            chat_id=group_id,
            photo=photo_id,
            caption=text,
            parse_mode="HTML",
            message_thread_id=thread_id
        )

        # =====================================================
        # VIDEO
        # =====================================================

    async def send_video_to_user(self, user_id: int, video_id: str, text: str):
        """Отпраляет пользователю видео (уже загруженнов в тг) и текст"""

        await self.bot.send_video(
            chat_id=user_id,
            video=video_id,
            caption=text,
            parse_mode="HTML"
        )

    async def send_video_to_group(self, group_id: int, video_id: str, text: str, thread_id: int or None = None):
        """Отпраляет в группу видео (уже загруженнов в тг) и текст"""
        await self.bot.send_video(
            chat_id=group_id,
            video=video_id,
            caption=text,
            parse_mode="HTML",
            message_thread_id=thread_id
        )

        # =====================================================
        # MEDIA GROUP
        # =====================================================

    async def send_media_group_to_user(self, user_id: int, media: list[dict], text: str):
        """
        media format:

        [
            {
                "type": "photo",
                "file_id": "..."
            },
            {
                "type": "video",
                "file_id": "..."
            }
        ]
        """

        media_group = []

        for index, item in enumerate(media):

            caption = text if index == 0 else None

            if item["type"] == "photo":

                media_group.append(
                    InputMediaPhoto(
                        media=item["file_id"],
                        caption=caption,
                        parse_mode="HTML"
                    )
                )

            elif item["type"] == "video":

                media_group.append(
                    InputMediaVideo(
                        media=item["file_id"],
                        caption=caption,
                        parse_mode="HTML"
                    )
                )

        await self.bot.send_media_group(
            chat_id=user_id,
            media=media_group
        )

    async def send_media_group_to_group(self, group_id: int, media: list[dict], text: str, thread_id: int or None = None):

        media_group = []

        for index, item in enumerate(media):

            caption = text if index == 0 else None

            if item["type"] == "photo":

                media_group.append(
                    InputMediaPhoto(
                        media=item["file_id"],
                        caption=caption,
                        parse_mode="HTML"
                    )
                )

            elif item["type"] == "video":

                media_group.append(
                    InputMediaVideo(
                        media=item["file_id"],
                        caption=caption,
                        parse_mode="HTML"
                    )
                )

        await self.bot.send_media_group(
            chat_id=group_id,
            media=media_group,
            message_thread_id=thread_id
        )