from dataclasses import dataclass


@dataclass
class User:
    tg_id: int
    first_name: str
    last_name: str
    role: int = 0  # 0 - гость, 1 - user, 2 - admin
    is_banned: bool = False
    failed_attempts: int = 0

    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()