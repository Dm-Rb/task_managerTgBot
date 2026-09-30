from sqlalchemy import DateTime, Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from database.base import Base
from datetime import datetime



class CashCollectionTaskTable(Base):
    __tablename__ = "cash_collection_task"


    id: Mapped[str] = mapped_column(String, primary_key=True)
    parent_id: Mapped[str] = mapped_column(String, nullable=False)    
    
    city_id: Mapped[int] = mapped_column(Integer, nullable=False)
    city: Mapped[str] = mapped_column(String, nullable=False)
    adress_id: Mapped[int] = mapped_column(Integer, nullable=False)
    adress: Mapped[str] = mapped_column(String, nullable=False)
    point_id: Mapped[int] = mapped_column(Integer, nullable=False)
    point: Mapped[str] = mapped_column(String, nullable=False)
    id_device: Mapped[str] = mapped_column(String, nullable=False)
    
    description: Mapped[str] = mapped_column(String, nullable=True)
    comment:  Mapped[str | None] = mapped_column(String, nullable=True)
    creator_id: Mapped[int] = mapped_column(Integer, nullable=False)
    creator_name: Mapped[str] = mapped_column(String, nullable=False)
    performer_id: Mapped[int] = mapped_column(Integer, nullable=False)
    performer_name: Mapped[str] = mapped_column(String, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    
    
    
