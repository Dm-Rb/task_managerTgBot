from telegram_bot.services.notification_service import NotificationService
from telegram_bot.services.task_service import TaskService
from telegram_bot.messages import task as messages_build
from telegram_bot.keyboards import update_task as keyboards
from telegram_bot.models.task import Task, TaskType, TaskStatus
from datetime import datetime, timezone


class TaskRuntimeService:

    def __init__(self, task_service: TaskService, notifications: NotificationService):
        self.task_service = task_service
        self.notifications = notifications

    def get_performer_tasks(self, performer_id: int) -> list[Task]:
        """Получить все Task связанные с исполнителем"""
        task_ids:list = self.task_service.indexes.get_performer_tasks(performer_id)

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
                reply_markup=keyboards.creator_task_keyboard(task.task_id)
            )

    async def register_new_task(
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
            is_active=True
    ) -> Task or None:
        """
        Создаёт задачу, сохраняет её и уведомляет исполнителя
        """
        # генерируем task_id
        #  создаём задачу через TaskService
        task = self.task_service.add_task(
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
            created_at=datetime.now(timezone.utc)
                    )
        if is_active:
            task_text = messages_build.get_notification_task_message('new', task)
            # Отправляем мессагу исполнителю с кнопкой Принять в работу
            keyboard_performer = keyboards.performer_task_keyboard(task.task_id, task.status)
            await self.notifications.send_to_user(user_id=performer_id, text=task_text, reply_markup=keyboard_performer)

            # Отправляем мессагу в группу (без кнопки)
            await self.notifications.send_to_group(group_id=group_id, text=task_text)
        return task

    async def accept_task(self, task_id: str) -> Task or None:

        task = self.task_service.get_task(task_id)

        if not task:
            return None

        # =====================================
        # Обновляем задачу
        # =====================================

        task.status = TaskStatus.IN_PROGRESS
        task.accepted_at = datetime.now(timezone.utc)

        self.task_service.upsert_task(task)

        # =====================================
        # Уведомления
        # =====================================
        if task.is_active:
            task_text = messages_build.get_notification_task_message('process', task)
            # Отправляем мессагу создателю без кнопки

            await self.notifications.send_to_user(user_id=task.creator_id, text=task_text)

            # Отправляем мессагу в группу (без кнопки)
            await self.notifications.send_to_group(group_id=task.group_id, text=task_text)
        return task

    async def cancel_task(self, task_id: str) -> Task or None:

        task = self.task_service.get_task(task_id)

        if not task:
            return None

        # Обновляем объект задачи
        task.status = TaskStatus.CANCELLED

        # удаляем задачу из кеша (объект задачи мы вернём)
        self.task_service.remove_task(task_id)

        # =====================================
        # Уведомления
        # =====================================
        if task.is_active:
            task_text = messages_build.get_notification_task_message('cancelled', task)
            # Отправляем мессагу исполнителю без кнопки
            await self.notifications.send_to_user(user_id=task.performer_id, text=task_text)

            # Отправляем мессагу в группу (без кнопки)
            await self.notifications.send_to_group(group_id=task.group_id, text=task_text)
        return task


