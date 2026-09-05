from database.models.task_tittle import TaskTittleTemplateTable


class TemplateCache:

    tittles: dict[int, TaskTittleTemplateTable] or dict = {}
    adresses: list[str] or list = []




