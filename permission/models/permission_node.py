from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class PermissionNode:
    node: str  # 权限节点
    value: bool  # 权限值
    priority: int = 0  # 优先级
    source: Optional[str] = None  # 权限来源
    expiry: Optional[int] = None  # 过期时间
    session: Optional[str] = None  # 会话限制

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'PermissionNode':
        return cls(**data)
