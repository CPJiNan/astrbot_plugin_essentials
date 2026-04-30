from typing import Dict, List, Optional, Set

from astrbot.api import logger

from ..models.placeholder_expansion import PlaceholderExpansion


class ExpansionManager:
    """占位符拓展管理器"""

    HEAD = '%'
    TAIL = '%'

    def __init__(self):
        self._expansions: Dict[str, PlaceholderExpansion] = {}

    def register(self, expansion: PlaceholderExpansion) -> bool:
        """注册占位符扩展"""
        identifier = expansion.identifier.lower()
        if not identifier or '_' in identifier:
            logger.warning(f"注册占位符扩展失败：标识符 {identifier} 无效。")
            return False
        if not expansion.can_register():
            logger.warning(f"注册占位符扩展失败：占位符 {identifier} 未满足注册条件。")
            return False
        if identifier in self._expansions:
            logger.warning(f"注册占位符扩展失败：标识符 {identifier} 已存在。")
            return False
        self._expansions[identifier] = expansion
        return True

    def unregister(self, identifier: str) -> bool:
        """注销占位符扩展"""
        identifier = identifier.lower()
        if identifier not in self._expansions:
            return False
        del self._expansions[identifier]
        return True

    def get_identifiers(self) -> Set[str]:
        """获取标识符列表"""
        return set(self._expansions.keys())

    def get_expansion(self, identifier: str) -> Optional[PlaceholderExpansion]:
        """获取占位符扩展"""
        return self._expansions.get(identifier.lower())

    def get_expansions(self) -> List[PlaceholderExpansion]:
        """获取占位符扩展列表"""
        return list(self._expansions.values())

    def is_registered(self, identifier: str) -> bool:
        """检查占位符是否已注册"""
        return identifier.lower() in self._expansions

    def set_placeholders(self, text: str) -> str:
        start = text.find(self.HEAD)
        if start == -1:
            return text

        length = len(text)
        builder = []
        cursor = 0

        while True:
            if start > cursor:
                builder.append(text[cursor:start])

            end = text.find(self.TAIL, start + 1)
            if end == -1:
                builder.append(text[start:length])
                return ''.join(builder)

            underscore = -1
            for i in range(start + 1, end):
                ch = text[i]
                if ch == ' ' and underscore == -1:
                    builder.append(self.HEAD)
                    cursor = start + 1
                    start = text.find(self.HEAD, cursor)
                    if start == -1:
                        builder.append(text[cursor:length])
                        return ''.join(builder)
                    break
                if ch == '_' and underscore == -1:
                    underscore = i
            else:
                if underscore == -1:
                    builder.append(text[start:end + 1])
                    cursor = end + 1
                    start = text.find(self.HEAD, cursor)
                    if start == -1:
                        break
                    continue

                identifier = text[start + 1:underscore]
                params = ""
                if underscore + 1 < end:
                    params = text[underscore + 1:end]

                expansion = self.get_expansion(identifier.lower())
                if expansion:
                    try:
                        replacement = expansion.on_request(params)
                    except Exception:
                        replacement = None
                else:
                    replacement = None

                if replacement is not None:
                    builder.append(replacement)
                else:
                    builder.append(self.HEAD)
                    builder.append(identifier)
                    builder.append('_')
                    builder.append(params)
                    builder.append(self.TAIL)

                cursor = end + 1
                start = text.find(self.HEAD, cursor)
                if start == -1:
                    break
                continue

            if start == -1:
                builder.append(text[cursor:length])
                return ''.join(builder)
            continue

        if cursor < length:
            builder.append(text[cursor:length])
        return ''.join(builder)
