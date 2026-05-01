from ..models.economy_data import EconomyData
from ...utils.storage import JsonStorage


class EconomyStorage:
    """经济存储"""

    def __init__(self, plugin):
        self.plugin = plugin
        self.json_storage = JsonStorage(plugin, "economy", EconomyData)
        self._cache = None

    async def initialize(self):
        """初始化经济存储"""
        await self.json_storage.initialize()
        self._cache = self.json_storage.get_data()

    async def load(self):
        """加载经济数据"""
        await self.json_storage.load()
        self._cache = self.json_storage.get_data()

    async def save(self):
        """保存经济数据"""
        await self.json_storage.save()

    def get_data(self) -> EconomyData:
        """获取经济数据"""
        return self._cache

    async def set_data(self, data: EconomyData):
        """设置经济数据"""
        await self.json_storage.set_data(data)
        self._cache = data
