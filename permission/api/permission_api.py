from typing import Optional, List

from astrbot.api import AstrBotConfig

from ..manager.permission_manager import PermissionManager
from ..models.group import Group
from ..models.permission_node import PermissionNode
from ..models.user import User


class PermissionAPI:
    def __init__(self, plugin, config: AstrBotConfig):
        self.plugin = plugin
        self.manager = PermissionManager(self.plugin, config)

    async def initialize(self):
        await self.manager.initialize()

    async def terminate(self):
        pass

    async def get_user(self, user_id: str) -> Optional[User]:
        """获取用户"""
        return await self.manager.get_user(user_id)

    async def get_users(self) -> List[User]:
        """获取用户列表"""
        return await self.manager.get_users()

    async def create_user(self, user_id: str) -> bool:
        """创建用户"""
        return await self.manager.create_user(user_id)

    async def delete_user(self, user_id: str) -> bool:
        """删除用户"""
        return await self.manager.delete_user(user_id)

    async def get_group(self, group_name: str) -> Optional[Group]:
        """获取权限组"""
        return await self.manager.get_group(group_name)

    async def get_groups(self) -> List[Group]:
        """获取权限组列表"""
        return await self.manager.get_groups()

    async def create_group(self, group_name: str, display: Optional[str] = None, weight: int = 0) -> bool:
        """创建权限组"""
        return await self.manager.create_group(group_name, display, weight)

    async def delete_group(self, group_name: str) -> bool:
        """删除权限组"""
        return await self.manager.delete_group(group_name)

    async def update_group(self, group_name: str, display: Optional[str] = None,
                           weight: Optional[int] = None, ) -> bool:
        """更新权限组"""
        return await self.manager.update_group(group_name, display, weight)

    async def get_user_permissions(self, user_id: str) -> List[PermissionNode]:
        """获取用户权限列表"""
        return await self.manager.get_user_permissions(user_id)

    async def has_user_permission(self, user_id: str, node: str, session: Optional[str] = None) -> bool:
        """检查用户权限是否存在"""
        return await self.manager.has_user_permission(user_id, node, session)

    async def add_user_permission(self, user_id: str, node: str, value: bool = True, priority: int = 0,
                                  source: Optional[str] = None, expiry: Optional[int] = None,
                                  session: Optional[str] = None) -> bool:
        """新增用户权限"""
        return await self.manager.add_user_permission(user_id, node, value, priority, source, expiry, session)

    async def remove_user_permission(self, user_id: str, node: str, session: Optional[str] = None) -> bool:
        """移除用户权限"""
        return await self.manager.remove_user_permission(user_id, node, session)

    async def get_group_permissions(self, group_name: str) -> List[PermissionNode]:
        """获取权限组权限列表"""
        return await self.manager.get_group_permissions(group_name)

    async def add_group_permission(self, group_name: str, node: str, value: bool = True, priority: int = 0,
                                   source: Optional[str] = None, expiry: Optional[int] = None,
                                   session: Optional[str] = None) -> bool:
        """新增权限组权限"""
        return await self.manager.add_group_permission(group_name, node, value, priority, source, expiry, session)

    async def remove_group_permission(self, group_name: str, node: str, session: Optional[str] = None) -> bool:
        """移除权限组权限"""
        return await self.manager.remove_group_permission(group_name, node, session)

    async def add_user_to_group(self, user_id: str, group_name: str) -> bool:
        """新增用户权限组"""
        return await self.manager.add_user_to_group(user_id, group_name)

    async def remove_user_from_group(self, user_id: str, group_name: str) -> bool:
        """移除用户权限组"""
        return await self.manager.remove_user_from_group(user_id, group_name)

    async def add_group_parent(self, group_name: str, parent_name: str) -> bool:
        """为权限组新增父权限组"""
        return await self.manager.add_group_parent(group_name, parent_name)

    async def remove_group_parent(self, group_name: str, parent_name: str) -> bool:
        """从权限组移除父权限组"""
        return await self.manager.remove_group_parent(group_name, parent_name)
