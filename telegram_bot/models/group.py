from dataclasses import dataclass, field


@dataclass
class Group:
    tg_id: int
    title: str
    is_admin: bool
    # members: list[int] = field(default_factory=list)