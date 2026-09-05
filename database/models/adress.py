from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from database.base import Base


class AdressTable(Base):
    __tablename__ = "adresses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    adress: Mapped[str] = mapped_column(String(500))
    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id"), nullable=False)
