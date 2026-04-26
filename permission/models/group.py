from dataclasses import dataclass, field
from typing import List, Optional

from .permission_node import PermissionNode


@dataclass
class Group:
    name: str  # 编辑名
    display: Optional[str] = None  # 展示名
    weight: int = 0  # 权重
    parents: List[str] = field(default_factory=list)  # 父权限组
    permissions: List[PermissionNode] = field(default_factory=list)  # 权限

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'display': self.display,
            'weight': self.weight,
            'parents': self.parents,
            'permissions': [permission.to_dict() for permission in self.permissions]
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Group':
        permissions = [PermissionNode.from_dict(permission) for permission in data.get('permissions', [])]
        return cls(
            name=data['name'],
            display=data.get('display'),
            weight=data.get('weight', 0),
            parents=data.get('parents', []),
            permissions=permissions
        )
