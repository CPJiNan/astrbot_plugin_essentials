import re
from dataclasses import dataclass, field
from typing import Any, Dict, List

from astrbot.api import logger, AstrBotConfig
from astrbot.api.event import AstrMessageEvent
from astrbot.api.star import Context
from astrbot.core.message.components import Plain, At
from astrbot.core.message.message_event_result import MessageChain
from astrbot.core.pipeline.waking_check.stage import WakingCheckStage


class PermissionProxy:
    def __init__(self, permission_api, context: Context, config: AstrBotConfig):
        self.permission_api = permission_api
        self.context = context
        self.enabled: bool = config.get("permission", {}).get("proxy", {}).get("enabled", False)
        self.rules: List[PermissionProxyRule] = []
        self._process = None
        self._injected = False
        self._load_rules(config)

    def _load_rules(self, config: AstrBotConfig):
        rules = config.get("permission", {}).get("proxy", {}).get("rules", [])
        for rule in rules:
            self.rules.append(PermissionProxyRule.from_dict(rule))
        logger.info(f"已加载 {len(self.rules)} 条权限代理规则。")

    async def check(self, event: AstrMessageEvent) -> bool:
        if event.get_sender_id() in self.context.get_config().get("admins_id", []):
            return True
        if not self.enabled:
            return True
        messages = []
        for component in event.get_messages():
            if isinstance(component, Plain):
                messages.append(component.text)
            elif isinstance(component, At):
                messages.append(f"@{component.name} ")
        message = "".join(messages)
        if not message:
            return True
        for rule in self.rules:
            if not rule.enabled:
                continue
            if not rule.match(message):
                continue
            if self.permission_api and await self.permission_api.has_user_permission(event.get_sender_id(), rule.node,
                                                                                     event.session_id):
                return True
            return False
        return True

    def inject(self):
        if self._injected:
            return
        self._process = WakingCheckStage.process

        async def injected_process(stage, event: AstrMessageEvent):
            if not await self.check(event):
                await event.send(MessageChain().message("无使用当前命令的权限。"))
                event.stop_event()
                return None
            return await self._process(stage, event)

        WakingCheckStage.process = injected_process
        self._injected = True
        logger.info("已向 WakingCheckStage 注入权限代理。")

    def eject(self):
        if self._injected and self._process:
            WakingCheckStage.process = self._process
            self._injected = False
            logger.info("已从 WakingCheckStage 移除权限代理。")


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
