from sqlalchemy import Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from database.base import Base


class TaskTittleTemplateTable(Base):
    __tablename__ = "task_tittle_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    tittle: Mapped[str] = mapped_column(String(400))
    is_sheduler: Mapped[bool] = mapped_column(Boolean, default=False)