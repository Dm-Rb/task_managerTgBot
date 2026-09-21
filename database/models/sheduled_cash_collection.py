from typing import Optional

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from database.base import Base




class ScheduledCashCollectionTable(Base):
    __tablename__ = "scheduled_cash_collection"


    id: Mapped[str] = mapped_column(String, primary_key=True)

    city_id: Mapped[int] = mapped_column(Integer, nullable=False)
    city: Mapped[str] = mapped_column(String, nullable=False)

    description: Mapped[str] = mapped_column(String, nullable=False)

    creator_id: Mapped[int] = mapped_column(Integer, nullable=False)
    creator_name: Mapped[str] = mapped_column(String, nullable=False)

    performer_id: Mapped[int] = mapped_column(Integer, nullable=False)
    performer_name: Mapped[str] = mapped_column(String, nullable=False)

    created_at: Mapped[DateTime] = mapped_column(DateTime)

    # Раз в сколько дней создавать задачу
    every_n_days: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )
    next_run_at: Mapped[DateTime] = mapped_column(DateTime)