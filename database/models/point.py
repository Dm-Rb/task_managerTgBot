from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from database.base import Base


class PointTable(Base):
    __tablename__ = "points"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    point: Mapped[str] = mapped_column(String(150)) 
    id_device: Mapped[str] = mapped_column(String(30))
    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id"), nullable=False)
    adress_id: Mapped[int] = mapped_column(ForeignKey("adresses.id"), nullable=False)
