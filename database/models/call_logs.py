from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from database.base import Base
from datetime import datetime


class CallTable(Base):
    __tablename__ = "call_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    from_: Mapped[str] = mapped_column(String(50))
    to_: Mapped[str | None] = mapped_column(String(50), nullable=True)
    short_text: Mapped[str] = mapped_column(String(500))
    text: Mapped[str] = mapped_column(String(2000))
    completed_at: Mapped[datetime] = mapped_column(DateTime)