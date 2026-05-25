from sqlalchemy.orm import Mapped, mapped_column
from database.base import Base

from sqlalchemy import (
    String,
    Integer,
    Boolean,
    DateTime,
    Text,
    BigInteger
)

from database.base import Base



class ScheduledTaskTable(Base):
    __tablename__ = "scheduled_tasks"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)

    group_id: Mapped[int] = mapped_column(BigInteger)
    topic_id: Mapped[int or None] = mapped_column(BigInteger, nullable=True)

    group_title: Mapped[str] = mapped_column(String)

    creator_id: Mapped[int] = mapped_column(BigInteger)
    creator_name: Mapped[str] = mapped_column(String)

    performer_id: Mapped[int] = mapped_column(BigInteger)
    performer_name: Mapped[str] = mapped_column(String)

    priority: Mapped[str] = mapped_column(String)

    address: Mapped[str or None] = mapped_column(String, nullable=True)

    task_type: Mapped[str] = mapped_column(String)

    created_at: Mapped[DateTime] = mapped_column(DateTime)

    every_n_days: Mapped[int or None] = mapped_column(Integer, nullable=True)

    next_run_at: Mapped[DateTime or None] = mapped_column(DateTime, nullable=True)