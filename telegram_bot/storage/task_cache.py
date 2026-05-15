from telegram_bot.models.task import Task, TaskTemplate, AddressTemplate


class TaskCache:

    def __init__(self):
        self.tasks: dict[str, Task] = {}
        self.task_templates: list[TaskTemplate] = []
        self.address_templates: list[AddressTemplate] = []

