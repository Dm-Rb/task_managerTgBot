from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from database.base import Base


class CityTable(Base):
    __tablename__ = "cities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    city: Mapped[str] = mapped_column(String(500)) 
    