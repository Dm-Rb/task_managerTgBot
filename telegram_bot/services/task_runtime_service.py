from telegram_bot.services.notification_service import NotificationService
from telegram_bot.services.task_service import TaskService
from telegram_bot.services.user_service import UserService

from telegram_bot.messages import task as messages_build
from telegram_bot.keyboards import update_task as keyboards
from telegram_bot.models.task import Task, TaskType, TaskStatus
from datetime import datetime, timezone, timedelta


class TaskRuntimeService:

    def __init__(self, task_service: TaskService, notifications: NotificationService, user_service: UserService):
        self.task_service = task_service
        self.notifications = notifications
        self.user_service = user_service

    def get_performer_tasks(self, performer_id: int) -> list[Task]:
        """Получить все Task связанные с исполнителем"""
        task_ids: list = self.task_service.indexes.get_performer_tasks(performer_id)

        return [
            task
            for task_id in task_ids
            if (task := self.task_service.get_task(task_id))
        ]

    def get_creator_tasks(self, creator_id: int) -> list[Task]:
        """Получить все Task связанные с создателем"""
        task_ids = self.task_service.indexes.get_creator_tasks(creator_id)

        return [
            task
            for task_id in task_ids
            if (task := self.task_service.get_task(task_id))
        ]

    async def send_tasks_to_performer(self, performer_id: int):
        """
        Отправляет все связанные задачи исполнителю в личные сообщения
        """
        tasks = self.get_performer_tasks(performer_id)
        if not tasks:
            await self.notifications.send_to_user(
                performer_id,
                "Пусто! У вас нет активных задач"
            )
            return

        for task in tasks:
            await self.notifications.send_to_user(
                user_id=performer_id,
                text=messages_build.get_task_message_by_task_obj(task),
                reply_markup=keyboards.performer_task_keyboard(
                    task.task_id,
                    task.status
                )
            )

    async def send_tasks_to_creator(self, creator_id: int):
        """
        Отправляет все связанные задачи создателю
        """
        tasks = self.get_creator_tasks(creator_id)

        if not tasks:
            await self.notifications.send_to_user(
                creator_id,
                "Пусто! У вас нет созданных задач"
            )
            return

        for task in tasks:
            await self.notifications.send_to_user(
                user_id=creator_id,
                text=messages_build.get_task_message_by_task_obj(task),
                reply_markup=keyboards.cancel_task_keyboard(task.task_id)
            )

    async def get_all_tasks(self, user_tg_id):
        """Получить все активные задачи за исклчением тех, где юзер является исполнителем. Это альтернатива send_tasks_to_creator.
        Разница в том, что показывает вообще все задачи а не только те, которые создал юзер"""
        tasks = [v for v in self.task_service.task_cache.values() if v.performer_id != user_tg_id]
        if not tasks:
            return await self.notifications.send_to_user(
                user_tg_id,
                "Пусто! Нет активных задач"
            )

        for task in tasks:
            await self.notifications.send_to_user(
                user_id=user_tg_id,
                text=messages_build.get_task_message_by_task_obj(task, user_tg_id),
                reply_markup=keyboards.cancel_task_keyboard(task.task_id)
            )

    async def get_all_scheduler_tasks(self, user_tg_id):
        """Получить все конфигурации задач по расписанию за исклчением тех, где юзер является исполнителем.
        """
        scheduler_tasks = [v for v in self.task_service.scheduler_task_cache.values() if v.performer_id != user_tg_id]
        if not scheduler_tasks:
            return await self.notifications.send_to_user(
                user_tg_id,
                "Пусто! Нет активных задач"
            )

        for scheduler_task in scheduler_tasks:
            await self.notifications.send_to_user(
                user_id=user_tg_id,
                text=messages_build.get_schedule_task_creation_message_by_state_schedule_task_obj(scheduler_task, user_tg_id),
                reply_markup=keyboards.cancel_scheduler_task_keyboard(scheduler_task.id)
            )

    async def register_new_task(self, task: Task) -> Task or None:
        """
        Создаёт задачу, сохраняет её и уведомляет исполнителя
        """

        task_text = messages_build.get_notification_task_message('new', task)
        task_text_for_creator = messages_build.get_notification_task_message('creator', task)
        # Отправляем мессагу создателю без кнопки
        await self.notifications.send_to_user(user_id=task.creator_id, text=task_text_for_creator)
        # Отправляем мессагу исполнителю с кнопкой Принять в работу
        keyboard_performer = keyboards.performer_task_keyboard(task.task_id, task.status)
        await self.notifications.send_to_user(user_id=task.performer_id, text=task_text, reply_markup=keyboard_performer)

        # Отправляем мессагу в группу (без кнопки) если исполнитель НЕ админ
        if not self.user_service.is_user_admin(task.performer_id):
            await self.notifications.send_to_group(group_id=task.group_id, text=task_text, thread_id=task.topic_id)
        return task

    async def accept_task(self, task_id: str) -> Task or None:

        task = self.task_service.get_task(task_id)

        if not task:
            return None

        # =====================================
        # Обновляем задачу
        # =====================================
        task.status = TaskStatus.IN_PROGRESS
        task.accepted_at = datetime.now()

        await self.task_service.upsert_task(task)

        # =====================================
        # Уведомления
        # =====================================
        task_text = messages_build.get_notification_task_message('process', task)
        # Отправляем мессагу создателю без кнопки
        await self.notifications.send_to_user(user_id=task.creator_id, text=task_text)

        # Отправляем мессагу в группу (без кнопки) если исполнитель НЕ админ
        if not self.user_service.is_user_admin(task.performer_id):
            await self.notifications.send_to_group(group_id=task.group_id, text=task_text, thread_id=task.topic_id)
        return task

    async def cancel_task(self, task_id: str) -> Task or None:

        task = self.task_service.get_task(task_id)

        if not task:
            return None

        # Обновляем объект задачи
        task.status = TaskStatus.CANCELLED

        # удаляем задачу из кеша (объект задачи мы вернём)
        await self.task_service.remove_task(task_id)

        # =====================================
        # Уведомления
        # =====================================
        if task.is_active:
            task_text = messages_build.get_notification_task_message('cancelled', task)
            # Отправляем мессагу исполнителю без кнопки
            await self.notifications.send_to_user(user_id=task.performer_id, text=task_text)
            # Отправляем мессагу в группу (без кнопки) если исполнитель НЕ админ
            if not self.user_service.is_user_admin(task.performer_id):
                await self.notifications.send_to_group(group_id=task.group_id, text=task_text, thread_id=task.topic_id)
            # # Отправляем мессагу в группу (без кнопки)
            # await self.notifications.send_to_group(group_id=task.group_id, text=task_text, thread_id=task.topic_id)
        return task

    async def complete_task(self, task_id: str, comment: str, media) -> Task or None:
        task: Task = self.task_service.get_task(task_id)

        if not task:
            return None

        # Обновляем объект задачи
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.now()
        task.is_active = False

        # удаляем задачу из кеша (объект задачи мы вернём)
        await self.task_service.remove_task(task_id)
        await self.task_service.task_database.upsert(task)
        # =====================================
        # Уведомления
        # =====================================
        task_text = messages_build.get_notification_task_message('completed', task)
        task_text += f"\n\n<b>Кoмментарий исполнителя:</b> <i>{comment}</i>"

        if len(media) == 1:
            media_item = media[0]
        # media_item = media[0]
            if media_item["type"] == "photo":
                # Отправляем мессагу создателю (без кнопки)
                await self.notifications.send_photo_to_user(task.creator_id, media_item["file_id"], task_text)
                # Отправляем мессагу исполнителю (без кнопки)
                await self.notifications.send_photo_to_user(task.performer_id, media_item["file_id"], task_text)
                # Отправляем мессагу в группу (без кнопки) если исполнитель НЕ админ
                if not self.user_service.is_user_admin(task.performer_id):
                    await self.notifications.send_photo_to_group(task.group_id, media_item["file_id"], task_text, task.topic_id)
            elif media_item["type"] == "video":
                # Отправляем мессагу создателю (без кнопки)
                await self.notifications.send_video_to_user(task.creator_id, media_item["file_id"], task_text)
                # Отправляем мессагу исполнителю
                await self.notifications.send_video_to_user(task.performer_id, media_item["file_id"], task_text)
                # Отправляем мессагу в группу (без кнопки) если исполнитель НЕ админ
                if not self.user_service.is_user_admin(task.performer_id):
                    await self.notifications.send_video_to_group(task.group_id, media_item["file_id"], task_text, task.topic_id)
        else:
            await self.notifications.send_media_group_to_user(user_id=task.creator_id, media=media, text=task_text)
            await self.notifications.send_media_group_to_user(user_id=task.performer_id, media=media, text=task_text)
            # Отправляем мессагу в группу (без кнопки) если исполнитель НЕ админ
            if not self.user_service.is_user_admin(task.performer_id):
                await self.notifications.send_media_group_to_group(group_id=task.group_id, media=media, text=task_text, thread_id=task.topic_id)
        # await self.notifications.send_to_group(group_id=task.group_id, text=task_text)
        return task

    async def register_new_schedule_task(
            self,
            title: str,
            description: str,
            group_id: int,
            group_title: str,
            creator_id: int,
            creator_name: str,
            performer_id: int,
            performer_name: str,
            priority: str,
            task_type: TaskType,
            every_n_days=None,
            address=None,
            topic_id=None,
            delay_hours=None
    ) -> Task or None:
        """
        Создаёт задачу, сохраняет её и уведомляет исполнителя
        """
        # генерируем task_id
        #  создаём задачу через TaskService
        if delay_hours:
            created_at = datetime.now().replace(second=0, microsecond=0)
            next_run_at = created_at + timedelta(hours=delay_hours)
        else:
            next_run_at = datetime.now().replace(second=0, microsecond=0)
        schedule_task = self.task_service.add_schedule(
            title=title,
            description=description,
            group_id=group_id,
            group_title=group_title,
            creator_id=creator_id,
            creator_name=creator_name,
            performer_id=performer_id,
            performer_name=performer_name,
            priority=priority,
            task_type=task_type,
            next_run_at=next_run_at,
            address=address,
            topic_id=topic_id,
            every_n_days=every_n_days
                    )
        return schedule_task


