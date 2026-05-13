from telegram_bot.models.task import Task


class TaskIndexes:
    """Хранит сввязи айдидишников между создатель - задача, исполнитель - задача. По-сути это реестр задач"""
    def __init__(self):
        # set вместо list что бы избежать дублирования при записи
        # {performer_user_id: set(task_id, task_id, ...), ...}
        self.performer_tasks: dict[int, set[str]] = {}  # исполнитель и задачи
        # {creator_user_id: set(task_id, task_id, ...), ...}
        self.creator_tasks: dict[int, set[str]] = {}  # создатель и задачи

    def register_task(self, task: Task):
        # созадаёт в словаре ключ task.performer_id и значение  task.task_id
        self.performer_tasks.setdefault(task.performer_id, set()).add(task.task_id)
        # аналогично
        self.creator_tasks.setdefault(task.creator_id, set()).add(task.task_id)

    def remove_task(self, task: Task):
        self.performer_tasks.get(task.performer_id, set()).discard(task.task_id)
        self.creator_tasks.get(task.creator_id, set()).discard(task.task_id)

    # GETTERS
    def get_performer_tasks(self, performer_id: int) -> list[str]:
        return list(self.performer_tasks.get(performer_id, []))

    def get_creator_tasks(self, creator_id: int) -> list[str]:
        return list(self.creator_tasks.get(creator_id, []))

