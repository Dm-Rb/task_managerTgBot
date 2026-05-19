from sqlalchemy import BigInteger, String, Boolean, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.base import Base


class Group(Base):

    __tablename__ = "groups"

    tg_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False)

    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    is_forum: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # relationship
    topics = relationship(
        "GroupTopic",
        back_populates="group",
        lazy="selectin",
        cascade="all, delete-orphan"
    )


# =========================================================
# GROUP TOPIC
# =========================================================

class GroupTopic(Base):

    __tablename__ = "group_topics"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    group_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("groups.tg_id", ondelete="CASCADE"),
        nullable=False
    )

    topic_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    topic_title: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    # relationship
    group = relationship(
        "Group",
        back_populates="topics"
    )

    # запрет дублей topic_id внутри группы
    __table_args__ = (
        UniqueConstraint(
            "group_id",
            "topic_id",
            name="uq_group_topic"
        ),
    )