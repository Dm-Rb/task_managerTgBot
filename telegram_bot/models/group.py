from dataclasses import dataclass, field


@dataclass
class Group:
    tg_id: int
    title: str
    is_admin: bool
    # members: list[int] = field(default_factory=list)

    # "г.Минск, ул.Мележа 1 (ТЦ Парус)"
    # "М. Институт культуры, цветы"
    #
    # "РЕМОНТ МОНЕТНИКА"
    # "Засор монетника"
    #
    # "Встретить посылку"
    # "В 18:30 приедет водитель"


