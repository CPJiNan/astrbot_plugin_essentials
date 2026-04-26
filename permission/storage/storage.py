from ..models.permissions_data import PermissionsData
from ...utils.storage import JsonStorage, KVStorage


class PermissionStorage:
    """权限存储"""

    def __init__(self, plugin):
        self.plugin = plugin
        self.json_storage = JsonStorage(plugin, "permissions", PermissionsData)
        self.kv_storage = KVStorage(plugin)
        self._cache = None

    async def initialize(self):
        """初始化权限存储"""
        await self.json_storage.initialize()
        self._cache = self.json_storage.get_data()

    async def load(self):
        """加载权限数据"""
        await self.json_storage.load()
        self._cache = self.json_storage.get_data()

    async def save(self):
        """保存权限数据"""
        await self.json_storage.save()

    def get_data(self) -> PermissionsData:
        """获取权限数据"""
        return self._cache

    async def set_data(self, data: PermissionsData):
        """设置权限数据"""
        await self.json_storage.set_data(data)
        self._cache = data

    async def get_kv_data(self, key: str, default=None):
        """获取 KV 数据"""
        return await self.kv_storage.get(key, default)

    async def put_kv_data(self, key: str, value):
        """设置 KV 数据"""
        await self.kv_storage.put(key, value)

    async def delete_kv_data(self, key: str):
        """删除 KV 数据"""
        await self.kv_storage.delete(key)
