from dataclasses import dataclass, field, asdict
from typing import Dict


@dataclass
class Account:
    user_id: str  # 用户 ID
    balances: Dict[str, int] = field(default_factory=dict)  # 货币 -> 余额

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'Account':
        return cls(**data)
