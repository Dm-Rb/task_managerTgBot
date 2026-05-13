from telegram_bot.models.task import Task, TaskTemplate


class TaskCache:

    def __init__(self):
        self.tasks: dict[str, Task] = {}
        self.templates: list[TaskTemplate] = []

