from telegram_bot.services.notification_service import NotificationService
from telegram_bot.services.cash_collection_service import CashCollectionService
from telegram_bot.services.user_service import UserService

from telegram_bot.messages import cash_collection as messages_build
from telegram_bot.keyboards import cash_collection as keyboards
from telegram_bot.models.cash_collection_task import CashCollectionTask, CashCollectionPoint


class CashCollectionRuntimeService:

    def __init__(self, 
                 cash_collection_service: CashCollectionService, 
                 notifications: NotificationService, 
                 user_service: UserService):
        self.cash_collection_service = cash_collection_service
        self.notifications = notifications
        self.user_service = user_service

    async def send_message_to_user(self, user_id: int, text: str, keyboard=None):
        """базовая функция отправки сообщения с детализацие задачи.
        отправляет ли текст или текст прикреплённым документом"""
        await self.notifications.send_to_user(
            user_id=user_id,
            text=text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )

    async def get_all_tasks_for_creator(self, user_tg_id):
        """Получить все активные задачи """
        tasks = [t for t in self.cash_collection_service.tasks.values() if t.creator_id == user_tg_id]

        if not tasks:
            return await self.notifications.send_to_user(
                user_tg_id,
                "Пусто! Нет активных задач по инкассации которые вы создали"
            )
        for task in tasks:
            text_message = messages_build.show_active_tasks_for_crearot(task)

            keyboard = keyboards.remove_task(task.parent_id)
            await self.send_message_to_user(user_tg_id, text_message, keyboard)
        return
    
    async def get_all_tasks_for_perfomer(self, user_tg_id: int):
        """базовая функция отправки сообщения с детализацие задачи.
        отправляет ли текст или текст прикреплённым документом"""
        # фильтруем задачи где user_tg_id является исполнителем и где есть хоть один point статус В процессе
        tasks = [t for t in self.cash_collection_service.tasks.values()
                    if t.performer_id == user_tg_id
                    and any(p.status == "В процессе" for p in t.points)
        ]

        if not tasks:
            return await self.notifications.send_to_user(
                user_tg_id,
                "Пусто! У вас нет активных задач по инкассации"
            )
        for task in tasks:
            text_message = messages_build.show_active_tasks_for_perfomer(task)
            keyboard = keyboards.show_points_for_perfomer(task)
            await self.send_message_to_user(user_tg_id, text_message, keyboard)
            
    async def register_new_task(self, task: CashCollectionTask) -> CashCollectionTask or None:
        """
        Создаёт задачу, сохраняет её и уведомляет исполнителя
        """
        text_for_creator = messages_build.new_cash_collection_task_for_crearot(task)
        text_for_performer = messages_build.new_cash_collection_task_for_performer(task)     
        
        # Отправляем мессагу создателю 
        # await self.notifications.send_to_user(user_id=task.creator_id, text=task_text_for_creator)
        await self.send_message_to_user(user_id=task.creator_id, text=text_for_creator)
        await self.send_message_to_user(user_id=task.performer_id, text=text_for_performer)
        
    async def сompleted_point_for_creator(self, task: CashCollectionTask, point: CashCollectionPoint) -> None:
        """
        Уведомляет создателя о завершении инкасации в пункте
        """
        text_for_creator = messages_build.completed_point_for_creator_msg(task, point)
        if not [p for p in task.points if p.status == "В процессе"]:
            text_for_creator += "\n✅ Инкассация всех пунктов в городе завершена"
        else:
            text_for_creator += "/show_cash_tasks"

        
        media_group = [
            {
                "type": "photo",
                "file_id": point.file_id_before
            },
                        {
                "type": "photo",
                "file_id": point.file_id_after
            }
        ]
        await self.notifications.send_media_group_to_user(user_id=task.creator_id, media=media_group, text=text_for_creator)




