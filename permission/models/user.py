from dataclasses import dataclass, field
from typing import List

from .permission_node import PermissionNode


@dataclass
class User:
    user_id: str  # ID
    groups: List[str] = field(default_factory=list)  # 权限组
    permissions: List[PermissionNode] = field(default_factory=list)  # 权限

    def to_dict(self) -> dict:
        return {
            'user_id': self.user_id,
            'groups': self.groups,
            'permissions': [permission.to_dict() for permission in self.permissions]
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        permissions = [PermissionNode.from_dict(permission) for permission in data.get('permissions', [])]
        return cls(
            user_id=data['user_id'],
            groups=data.get('groups', []),
            permissions=permissions
        )
