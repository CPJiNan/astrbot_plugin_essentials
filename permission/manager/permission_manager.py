import time
from typing import List, Optional, Set

from astrbot.api import logger, AstrBotConfig

from ..models.group import Group
from ..models.permission_node import PermissionNode
from ..models.user import User
from ..storage import PermissionStorage
from ...utils.cache import SimpleCache


class PermissionManager:
    """权限管理器"""

    def __init__(self, plugin, config: AstrBotConfig):
        self.plugin = plugin
        self.storage = PermissionStorage(plugin)
        self.cache = SimpleCache(default_expiry=config.get("permission", {}).get("cache_default_expiry", 300))

    async def initialize(self):
        await self.storage.initialize()

    async def terminate(self):
        pass

    async def get_user(self, user_id: str) -> Optional[User]:
        """获取用户"""
        return self.storage.get_data().users.get(user_id)

    async def get_users(self) -> List[User]:
        """获取用户列表"""
        return list(self.storage.get_data().users.values())

    async def create_user(self, user_id: str) -> bool:
        """创建用户"""
        try:
            data = self.storage.get_data()
            if user_id in data.users:
                return False
            data.users[user_id] = User(user_id=user_id)
            await self.storage.save()
            self.cache.clear_prefix(f"{user_id}:")
            return True
        except Exception as e:
            logger.error(f"创建用户失败：{e}。")
            return False

    async def delete_user(self, user_id: str) -> bool:
        """删除用户"""
        try:
            data = self.storage.get_data()
            if user_id not in data.users:
                return False
            del data.users[user_id]
            await self.storage.save()
            self.cache.clear_prefix(f"{user_id}:")
            return True
        except Exception as e:
            logger.error(f"删除用户失败：{e}。")
            return False

    async def get_group(self, group_name: str) -> Optional[Group]:
        """获取权限组"""
        return self.storage.get_data().groups.get(group_name)

    async def get_groups(self) -> List[Group]:
        """获取权限组列表"""
        return list(self.storage.get_data().groups.values())

    async def create_group(self, group_name: str, display: Optional[str] = None, weight: int = 0) -> bool:
        """创建权限组"""
        try:
            data = self.storage.get_data()
            if group_name in data.groups:
                return False
            data.groups[group_name] = Group(name=group_name, display=display, weight=weight)
            await self.storage.save()
            return True
        except Exception as e:
            logger.error(f"创建权限组失败：{e}。")
            return False

    async def delete_group(self, group_name: str) -> bool:
        """删除权限组"""
        try:
            data = self.storage.get_data()
            if group_name not in data.groups:
                return False
            for user in data.users.values():
                if group_name in user.groups:
                    user.groups.remove(group_name)
            for group in data.groups.values():
                if group_name in group.parents:
                    group.parents.remove(group_name)
            del data.groups[group_name]
            await self.storage.save()
            self.cache.clear()
            return True
        except Exception as e:
            logger.error(f"删除权限组失败：{e}。")
            return False

    async def update_group(
            self,
            group_name: str,
            display: Optional[str] = None,
            weight: Optional[int] = None
    ) -> bool:
        """更新权限组"""
        try:
            data = self.storage.get_data()
            if group_name not in data.groups:
                return False
            group = data.groups[group_name]
            if weight is not None:
                group.weight = weight
            if display is not None:
                group.display = display
            await self.storage.save()
            self.cache.clear()
            return True
        except Exception as e:
            logger.error(f"更新权限组失败：{e}。")
            return False

    async def get_user_permissions(self, user_id: str) -> List[PermissionNode]:
        """获取用户权限列表"""
        user = await self.get_user(user_id)
        return user.permissions.copy() if user else []

    async def has_user_permission(
            self,
            user_id: str,
            node: str,
            session: Optional[str] = None
    ) -> bool:
        """检查用户权限"""
        data = self.storage.get_data()

        cache_key = f"{user_id}:{node}:{session or 'global'}"
        cached: Optional[bool] = self.cache.get(cache_key)
        if cached is not None:
            return cached

        user = data.users.get(user_id)
        if not user:
            user_permissions: List[PermissionNode] = []
            groups: List[str] = []
        else:
            user_permissions = user.permissions
            groups = list(user.groups)

        all_permissions: List[PermissionNode] = []
        all_permissions.extend(user_permissions)

        visited: Set[str] = set()

        def get_group_permissions(name: str) -> None:
            if name in visited:
                return
            visited.add(name)
            group = data.groups.get(name)
            if not group:
                return
            all_permissions.extend(group.permissions)
            for parent in group.parents:
                get_group_permissions(parent)

        for group_name in groups:
            get_group_permissions(group_name)

        sorted_permissions = sorted(all_permissions, key=lambda n: n.priority, reverse=True)
        result = False
        cache_expiry = None
        for permission in sorted_permissions:
            if not (node == permission.node or
                    (permission.node.endswith('*') and node.startswith(permission.node[:-1]))):
                continue
            if permission.expiry and permission.expiry < time.time():
                continue
            if permission.session and permission.session != session:
                continue
            result = permission.value
            cache_expiry = permission.expiry
            break
        if result:
            if cache_expiry:
                cache_ttl = max(1, int(cache_expiry - time.time()))
            else:
                cache_ttl = self.cache.default_expiry
            self.cache.set(cache_key, result, cache_ttl)
        return result

    async def add_user_permission(
            self,
            user_id: str,
            node: str,
            value: bool = True,
            priority: int = 0,
            source: Optional[str] = None,
            expiry: Optional[int] = None,
            session: Optional[str] = None,
    ) -> bool:
        """新增用户权限"""
        try:
            data = self.storage.get_data()
            if user_id not in data.users:
                data.users[user_id] = User(user_id=user_id)
            user = data.users[user_id]
            index = next(
                (i for i, p in enumerate(user.permissions)
                 if p.node == node and p.session == session),
                None
            )
            permission_node = PermissionNode(
                node=node,
                value=value,
                priority=priority,
                source=source,
                expiry=expiry,
                session=session,
            )
            if index is not None:
                user.permissions[index] = permission_node
            else:
                user.permissions.append(permission_node)
            await self.storage.save()
            self.cache.clear_prefix(f"{user_id}:")
            return True
        except Exception as e:
            logger.error(f"新增用户权限失败：{e}。")
            return False

    async def remove_user_permission(
            self,
            user_id: str,
            node: str,
            session: Optional[str] = None
    ) -> bool:
        """移除用户权限"""
        try:
            data = self.storage.get_data()
            if user_id not in data.users:
                return False
            user = data.users[user_id]
            index = next(
                (i for i, permission in enumerate(user.permissions)
                 if permission.node == node and permission.session == session),
                None
            )
            if index is not None:
                user.permissions.pop(index)
                await self.storage.save()
                self.cache.clear_prefix(f"{user_id}:")
                return True
            return False
        except Exception as e:
            logger.error(f"移除用户权限失败：{e}。")
            return False

    async def get_group_permissions(self, group_name: str) -> List[PermissionNode]:
        """获取权限组权限列表"""
        group = await self.get_group(group_name)
        return group.permissions.copy() if group else []

    async def add_group_permission(
            self,
            group_name: str,
            node: str,
            value: bool = True,
            priority: int = 0,
            source: Optional[str] = None,
            expiry: Optional[int] = None,
            session: Optional[str] = None,
    ) -> bool:
        """新增权限组权限"""
        try:
            data = self.storage.get_data()
            if group_name not in data.groups:
                return False
            group = data.groups[group_name]
            index = next(
                (i for i, permission in enumerate(group.permissions)
                 if permission.node == node and permission.session == session),
                None
            )
            permission_node = PermissionNode(
                node=node,
                value=value,
                priority=priority,
                source=source,
                expiry=expiry,
                session=session,
            )
            if index is not None:
                group.permissions[index] = permission_node
            else:
                group.permissions.append(permission_node)
            await self.storage.save()
            self.cache.clear()
            return True
        except Exception as e:
            logger.error(f"新增权限组权限失败：{e}。")
            return False

    async def remove_group_permission(
            self,
            group_name: str,
            node: str,
            session: Optional[str] = None
    ) -> bool:
        """移除权限组权限"""
        try:
            data = self.storage.get_data()
            if group_name not in data.groups:
                return False
            group = data.groups[group_name]
            index = next(
                (i for i, permission in enumerate(group.permissions)
                 if permission.node == node and permission.session == session),
                None
            )
            if index is not None:
                group.permissions.pop(index)
                await self.storage.save()
                self.cache.clear()
                return True
            return False
        except Exception as e:
            logger.error(f"移除权限组权限失败：{e}。")
            return False

    async def add_user_to_group(self, user_id: str, group_name: str) -> bool:
        """新增用户权限组"""
        try:
            data = self.storage.get_data()
            if group_name not in data.groups:
                return False
            if user_id not in data.users:
                data.users[user_id] = User(user_id=user_id)
            user = data.users[user_id]
            if group_name not in user.groups:
                user.groups.append(group_name)
                await self.storage.save()
                self.cache.clear_prefix(f"{user_id}:")
                return True
            return False
        except Exception as e:
            logger.error(f"新增用户权限组失败：{e}。")
            return False

    async def remove_user_from_group(self, user_id: str, group_name: str) -> bool:
        """移除用户权限组"""
        try:
            data = self.storage.get_data()
            if user_id not in data.users:
                return False
            user = data.users[user_id]
            if group_name in user.groups:
                user.groups.remove(group_name)
                await self.storage.save()
                self.cache.clear_prefix(f"{user_id}:")
                return True
            return False
        except Exception as e:
            logger.error(f"移除用户权限组户失败：{e}。")
            return False

    async def add_group_parent(self, group_name: str, parent_name: str) -> bool:
        """为权限组新增父权限组"""
        try:
            data = self.storage.get_data()
            if group_name not in data.groups or parent_name not in data.groups:
                return False

            def dfs(current: str, visited: set) -> bool:
                if current == group_name:
                    return True
                if current in visited:
                    return False
                visited.add(current)
                current_group = data.groups.get(current)
                if not current_group:
                    return False
                for parent in current_group.parents:
                    if dfs(parent, visited.copy()):
                        return True
                return False

            if dfs(parent_name, set()):
                logger.warning(f"为权限组新增父权限组失败：存在循环继承 {group_name} <- {parent_name}。")
                return False

            group = data.groups[group_name]
            if parent_name not in group.parents:
                group.parents.append(parent_name)
                await self.storage.save()
                self.cache.clear()
                return True
            return False
        except Exception as e:
            logger.error(f"为权限组新增父权限组失败：{e}。")
            return False

    async def remove_group_parent(self, group_name: str, parent_name: str) -> bool:
        """从权限组移除父权限组"""
        try:
            data = self.storage.get_data()
            if group_name not in data.groups:
                return False
            group = data.groups[group_name]
            if parent_name in group.parents:
                group.parents.remove(parent_name)
                await self.storage.save()
                self.cache.clear()
                return True
            return False
        except Exception as e:
            logger.error(f"从权限组移除父权限组失败：{e}。")
            return False
