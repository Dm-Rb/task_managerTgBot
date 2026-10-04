from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from database.base import Base
from datetime import datetime


class SmsTable(Base):
    __tablename__ = "sms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    from_: Mapped[str] = mapped_column(String(50))
    text: Mapped[str] = mapped_column(String(500))
    sentStamp: Mapped[str] = mapped_column(String(50))
    completed_at: Mapped[datetime] = mapped_column(DateTime)