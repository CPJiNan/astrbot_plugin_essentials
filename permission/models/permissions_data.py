from dataclasses import dataclass
from typing import Dict

from .group import Group
from .user import User


@dataclass
class PermissionsData:
    users: Dict[str, User] = None  # 用户数据
    groups: Dict[str, Group] = None  # 权限组数据

    def __post_init__(self):
        if self.users is None:
            self.users = {}
        if self.groups is None:
            self.groups = {}

    def to_dict(self) -> dict:
        return {
            'users': {user_id: user.to_dict() for user_id, user in self.users.items()},
            'groups': {group_name: group.to_dict() for group_name, group in self.groups.items()}
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'PermissionsData':
        users = {user_id: User.from_dict(user_data) for user_id, user_data in data.get('users', {}).items()}
        groups = {group_name: Group.from_dict(group_data) for group_name, group_data in data.get('groups', {}).items()}
        return cls(users=users, groups=groups)
