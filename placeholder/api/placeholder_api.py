from typing import Callable, Optional, Set

from ..manager.expansion_manager import ExpansionManager


class PlaceholderAPI:

    def __init__(self, plugin):
        self.plugin = plugin
        self.manager = ExpansionManager()

    async def initialize(self):
        pass

    async def terminate(self):
        pass

    def register(self, identifier: str, handler: Callable[[str], Optional[str]]) -> bool:
        """注册占位符扩展"""
        return self.manager.register(identifier, handler)

    def unregister(self, identifier: str) -> bool:
        """注销占位符扩展"""
        return self.manager.unregister(identifier)

    def get_identifiers(self) -> Set[str]:
        """获取标识符列表"""
        return self.manager.get_identifiers()

    def is_registered(self, identifier: str) -> bool:
        """检查标识符是否已注册"""
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
