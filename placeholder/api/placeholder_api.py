from typing import List, Optional, Set

from ..manager.expansion_manager import ExpansionManager
from ..models import PlaceholderExpansion


class PlaceholderAPI:

    def __init__(self, plugin):
        self.plugin = plugin
        self.manager = ExpansionManager()

    async def initialize(self):
        pass

    async def terminate(self):
        pass

    def register(self, expansion: PlaceholderExpansion) -> bool:
        """注册占位符扩展"""
        return self.manager.register(expansion)

    def unregister(self, identifier: str) -> bool:
        """注销占位符扩展"""
        return self.manager.unregister(identifier)

    def get_identifiers(self) -> Set[str]:
        """获取标识符列表"""
        return self.manager.get_identifiers()

    def get_expansion(self, identifier: str) -> Optional[PlaceholderExpansion]:
        """获取占位符扩展"""
        return self.manager.get_expansion(identifier)

    def get_expansions(self) -> List[PlaceholderExpansion]:
        """获取占位符扩展列表"""
        return self.manager.get_expansions()

    def is_registered(self, identifier: str) -> bool:
        """检查占位符是否已注册"""
        return self.manager.is_registered(identifier)

    def set_placeholders(self, text: str) -> str:
        """解析文本中的占位符"""
        return self.manager.set_placeholders(text)

    def contains_placeholders(self, text: str) -> bool:
        """检查文本中是否包含占位符"""
        if not text:
            return False
        first = text.find('%')
        if first == -1:
            return False
        return text.find('%', first + 1) != -1
