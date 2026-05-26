from io import BytesIO
from datetime import datetime

from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter

from aiogram.types import BufferedInputFile


async def export_completed_tasks_report(repository):
    """
    Генерация XLSX отчёта в памяти
    без сохранения на диск
    """

    tasks = await repository.get_completed_tasks_last_30_days()

    # ==========================================
    # CREATE WORKBOOK
    # ==========================================

    wb = Workbook()
    ws = wb.active

    ws.title = "Completed Tasks"

    # ==========================================
    # HEADERS
    # ==========================================

    headers = [
        "Задача",
        "Описание задачи",
        "Группа",
        "Создатель",
        "Исполнитель",
        "Приоритет",
        "Тип",
        "Дата/время создания",
        "Время реагирования",
        "Время выполнения"
    ]

    ws.append(headers)

    # ==========================================
    # HEADER STYLE
    # ==========================================

    for cell in ws[1]:
        cell.font = Font(bold=True)

    # ==========================================
    # ROWS
    # ==========================================

    for task in tasks:

        # ==========================================
        # CREATED AT
        # ==========================================

        created_at = ""

        if task.created_at:
            created_at = task.created_at.strftime(
                "%d.%m.%Y %H:%M"
            )

        # ==========================================
        # REACTION TIME
        # ==========================================

        reaction_time = "-"

        if task.accepted_at and task.created_at:

            delta = task.accepted_at - task.created_at

            total_seconds = int(delta.total_seconds())

            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60

            reaction_time = f"{hours:02}:{minutes:02}"

            if reaction_time == "00:00":
                reaction_time = "Мгновенно"

        # ==========================================
        # EXECUTION TIME
        # ==========================================

        execution_time = "-"

        if task.accepted_at and task.completed_at:

            delta = task.completed_at - task.accepted_at

            total_seconds = int(delta.total_seconds())

            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60

            execution_time = f"{hours:02}:{minutes:02}"

            if execution_time == "00:00":
                execution_time = "Мгновенно"

        # ==========================================
        # APPEND ROW
        # ==========================================

        ws.append([
            task.title,
            task.description,
            task.group_title,
            task.creator_name,
            task.performer_name,
            task.priority,
            task.task_type,
            created_at,
            reaction_time,
            execution_time
        ])

    # ==========================================
    # AUTO WIDTH
    # ==========================================

    for column_cells in ws.columns:

        length = 0
        column = column_cells[0].column

        for cell in column_cells:

            try:
                if cell.value:
                    length = max(length, len(str(cell.value)))
            except:
                pass

        adjusted_width = min(length + 5, 60)

        ws.column_dimensions[
            get_column_letter(column)
        ].width = adjusted_width

    # ==========================================
    # SAVE TO MEMORY
    # ==========================================

    file_stream = BytesIO()

    wb.save(file_stream)

    file_stream.seek(0)

    filename = (
        f"completed_tasks_report_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    )

    return BufferedInputFile(
        file=file_stream.read(),
        filename=filename
    )