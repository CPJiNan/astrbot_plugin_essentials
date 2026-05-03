import re
from dataclasses import dataclass, field
from typing import Any, Dict, List

from astrbot.api import logger, AstrBotConfig
from astrbot.api.event import AstrMessageEvent


class PermissionProxy:
    def __init__(self, permission_api, config: AstrBotConfig):
        self.permission_api = permission_api
        self.enabled: bool = config.get("proxy", {}).get("enabled", True)
        self.rules: List[PermissionProxyRule] = []
        self._load_rules(config)

    def _load_rules(self, config: AstrBotConfig):
        rules = config.get("proxy", {}).get("rules", [])
        for rule in rules:
            self.rules.append(PermissionProxyRule.from_dict(rule))
        logger.info(f"已加载 {len(self.rules)} 条权限代理规则。")

    async def check(self, event: AstrMessageEvent) -> bool:
        if not self.enabled:
            return True
        message = event.message_str
        if not message:
            return True
        for rule in self.rules:
            if not rule.enabled:
                continue
            if not rule.match(message):
                continue
            if event.is_admin():
                return True
            if self.permission_api and await self.permission_api.has_user_permission(event.get_sender_id(), rule.node,
                                                                                     event.session_id):
                return True
            return False
        return True


@dataclass
class PermissionProxyRule:
    name: str = ""
    enabled: bool = True
    keywords: List[str] = field(default_factory=list)
    node: str = ""

    def __post_init__(self):
        self._compiled_patterns: List[re.Pattern] = []
        self._compile_patterns()

    def _compile_patterns(self):
        self._compiled_patterns.clear()
        for pattern in self.keywords:
            if not pattern.strip():
                continue
            try:
                self._compiled_patterns.append(re.compile(pattern))
            except re.error:
                logger.warning(f"权限代理规则 {self.name} 中的正则表达式 {pattern} 无效。")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PermissionProxyRule":
        return cls(
            name=data.get("name", ""),
            enabled=data.get("enabled", True),
            keywords=data.get("keywords", []),
            node=data.get("node", ""),
        )

    def match(self, message: str) -> bool:
        if not self.enabled or not self._compiled_patterns:
            return False
        for pattern in self._compiled_patterns:
            if pattern.search(message):
                return True
        return False
