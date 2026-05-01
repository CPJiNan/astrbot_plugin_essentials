from astrbot.api import AstrBotConfig

from ..manager.economy_manager import EconomyManager


class EconomyAPI:
    def __init__(self, plugin, config: AstrBotConfig):
        self.plugin = plugin
        self.manager = EconomyManager(self.plugin, config)

    async def initialize(self):
        await self.manager.initialize()

    async def terminate(self):
        pass

    async def get_balance(self, user_id: str, currency: str) -> int:
        """获取用户余额"""
        return await self.manager.get_balance(user_id, currency)

    async def has_account(self, user_id: str) -> bool:
        """检查用户账户是否存在"""
        return await self.manager.has_account(user_id)

    async def create_account(self, user_id: str) -> bool:
        """创建用户账户"""
        return await self.manager.create_account(user_id)

    async def delete_account(self, user_id: str) -> bool:
        """删除用户账户"""
        return await self.manager.delete_account(user_id)

    async def set_balance(self, user_id: str, currency: str, amount: int) -> bool:
        """设置用户余额"""
        return await self.manager.set_balance(user_id, currency, amount)

    async def add_balance(self, user_id: str, currency: str, amount: int) -> bool:
        """增加用户余额"""
        return await self.manager.add_balance(user_id, currency, amount)

    async def remove_balance(self, user_id: str, currency: str, amount: int) -> bool:
        """减少用户余额"""
        return await self.manager.remove_balance(user_id, currency, amount)
