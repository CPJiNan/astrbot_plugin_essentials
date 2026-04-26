import json
from typing import Optional, TypeVar, Generic

from astrbot.api.star import StarTools

T = TypeVar('T')


class JsonStorage(Generic[T]):
    """JSON 存储"""

    def __init__(self, plugin, storage_name: str, data_class: type[T]):
        self.plugin = plugin
        self.data_class = data_class
        self.data_path = StarTools.get_data_dir(self.plugin.name)
        self.storage_name = storage_name
        self.storage_file = self.data_path / f"{storage_name}.json"
        self._cache: Optional[T] = None

    async def initialize(self):
        """初始化 JSON 存储"""
        self.data_path.mkdir(parents=True, exist_ok=True)
        await self.load()

    async def load(self):
        """加载 JSON 数据"""
        try:
            if self.storage_file.exists():
                with open(self.storage_file, 'r', encoding='utf-8') as file:
                    self._cache = self.data_class.from_dict(json.load(file))
            else:
                self._cache = self.data_class()
        except Exception as e:
            self.plugin.logger.error(f"加载 {self.storage_name} 数据失败：{e}。")
            self._cache = self.data_class()

    async def save(self):
        """保存 JSON 数据"""
        try:
            if self._cache:
                data = self._cache.to_dict()
                with open(self.storage_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.plugin.logger.error(f"保存 {self.storage_name} 数据失败：{e}。")

    def get_data(self) -> T:
        """获取 JSON 数据"""
        return self._cache

    async def set_data(self, data: T):
        """设置 JSON 数据"""
        self._cache = data
        await self.save()


class KVStorage:
    """KV 存储"""

    def __init__(self, plugin):
        self.plugin = plugin

    async def get(self, key: str, default=None):
        """获取 KV 数据"""
        return await self.plugin.get_kv_data(key, default)

    async def put(self, key: str, value):
        """设置 KV 数据"""
        await self.plugin.put_kv_data(key, value)

    async def delete(self, key: str):
        """删除 KV 数据"""
        await self.plugin.delete_kv_data(key)
