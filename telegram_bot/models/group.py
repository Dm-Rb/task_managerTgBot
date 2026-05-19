from dataclasses import dataclass, field
from typing import Optional


@dataclass
class GroupTopic:
    topic_id: int
    title: str


@dataclass
class Group:
    tg_id: int
    title: str

    is_admin: bool = False

    # support forum groups
    is_forum: bool = False

    # список топиков
    topics: list[GroupTopic] = field(default_factory=list)
