from typing import Callable, Dict, Optional, Set

from astrbot.api import logger


class ExpansionManager:
    """占位符拓展管理器"""

    HEAD = '%'
    TAIL = '%'

    def __init__(self):
        self._handlers: Dict[str, Callable[[str], Optional[str]]] = {}

    def register(self, identifier: str, handler: Callable[[str], Optional[str]]) -> bool:
        identifier = identifier.lower()
        if not identifier or '_' in identifier:
            logger.warning(f"注册占位符扩展失败：标识符 {identifier} 无效。")
            return False
        if identifier in self._handlers:
            logger.warning(f"注册占位符扩展失败：标识符 {identifier} 已存在。")
            return False
        self._handlers[identifier] = handler
        return True

    def unregister(self, identifier: str) -> bool:
        identifier = identifier.lower()
        if identifier not in self._handlers:
            return False
        del self._handlers[identifier]
        return True

    def get_handler(self, identifier: str) -> Optional[Callable[[str], Optional[str]]]:
        return self._handlers.get(identifier.lower())

    def get_identifiers(self) -> Set[str]:
        return set(self._handlers.keys())

    def is_registered(self, identifier: str) -> bool:
        return identifier.lower() in self._handlers

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

                handler = self.get_handler(identifier.lower())
                replacement = handler(params) if handler else None

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
