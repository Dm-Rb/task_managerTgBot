from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import (
    String,
    Integer,
    Boolean,
    DateTime,
    Text
)

from database.base import Base
from datetime import datetime


class TaskTable(Base):

    __tablename__ = "tasks"

    # ==========================================
    # PRIMARY KEY
    # ==========================================

    task_id: Mapped[str] = mapped_column(
        String(32),
        primary_key=True
    )

    # ==========================================
    # BASIC INFO
    # ==========================================

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    # ==========================================
    # GROUP
    # ==========================================

    group_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True
    )

    group_title: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    # ==========================================
    # CREATOR
    # ==========================================

    creator_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True
    )

    creator_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    # ==========================================
    # PERFORMER
    # ==========================================

    performer_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True
    )

    performer_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    # ==========================================
    # TASK SETTINGS
    # ==========================================

    priority: Mapped[str] = mapped_column(
        String(32),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="Новая"
    )

    task_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="Разово"
    )

    # ==========================================
    # DATES
    # ==========================================

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )

    accepted_at: Mapped[datetime or None] = mapped_column(
        DateTime,
        nullable=True
    )

    completed_at: Mapped[datetime or None] = mapped_column(
        DateTime,
        nullable=True
    )

    # ==========================================
    # RECURRING TASKS
    # ==========================================

    recurrence_interval: Mapped[str or None] = mapped_column(
        String(64),
        nullable=True
    )

    every_n: Mapped[int or None] = mapped_column(
        Integer,
        nullable=True
    )

    next_execution_at: Mapped[datetime or None] = mapped_column(
        DateTime,
        nullable=True
    )

    parent_task_id: Mapped[str or None] = mapped_column(
        String(32),
        nullable=True,
        index=True
    )

    # ==========================================
    # FLAGS
    # ==========================================

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
    )