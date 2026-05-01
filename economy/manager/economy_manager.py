from typing import Optional

from astrbot.api import logger, AstrBotConfig

from ..models.account import Account
from ..storage import EconomyStorage
from ...utils.cache import SimpleCache


class EconomyManager:
    """经济管理器"""

    def __init__(self, plugin, config: AstrBotConfig):
        self.plugin = plugin
        self.storage = EconomyStorage(plugin)
        self.cache = SimpleCache(default_expiry=config.get("economy", {}).get("cache_default_expiry", 300))

    async def initialize(self):
        await self.storage.initialize()

    async def terminate(self):
        pass

    async def get_balance(self, user_id: str, currency: str) -> int:
        """获取用户余额"""
        cache_key = f"{user_id}:{currency}:balance"
        cached: Optional[int] = self.cache.get(cache_key)
        if cached is not None:
            return cached

        data = self.storage.get_data()
        account = data.accounts.get(user_id)
        balance = account.balances.get(currency, 0) if account else 0
        self.cache.set(cache_key, balance)
        return balance

    async def has_account(self, user_id: str) -> bool:
        """检查用户账户是否存在"""
        cache_key = f"{user_id}:exists"
        cached: Optional[bool] = self.cache.get(cache_key)
        if cached is not None:
            return cached

        data = self.storage.get_data()
        exists = user_id in data.accounts
        self.cache.set(cache_key, exists)
        return exists

    async def create_account(self, user_id: str) -> bool:
        """创建用户账户"""
        try:
            data = self.storage.get_data()
            if user_id in data.accounts:
                return False
            data.accounts[user_id] = Account(user_id=user_id)
            await self.storage.save()
            self.cache.clear_prefix(f"{user_id}:")
            return True
        except Exception as e:
            logger.error(f"创建用户账户失败：{e}。")
            return False

    async def delete_account(self, user_id: str) -> bool:
        """删除用户账户"""
        try:
            data = self.storage.get_data()
            if user_id not in data.accounts:
                return False
            del data.accounts[user_id]
            await self.storage.save()
            self.cache.clear_prefix(f"{user_id}:")
            return True
        except Exception as e:
            logger.error(f"删除用户账户失败：{e}。")
            return False

    async def set_balance(self, user_id: str, currency: str, amount: int) -> bool:
        """设置用户余额"""
        try:
            if not await self.has_account(user_id):
                await self.create_account(user_id)
            data = self.storage.get_data()
            account = data.accounts.get(user_id)
            account.balances[currency] = amount
            await self.storage.save()
            self.cache.clear_prefix(f"{user_id}:")
            return True
        except Exception as e:
            logger.error(f"设置用户余额失败：{e}。")
            return False

    async def add_balance(self, user_id: str, currency: str, amount: int) -> bool:
        """增加用户余额"""
        if amount <= 0:
            return False
        if not await self.has_account(user_id):
            await self.create_account(user_id)
        current = await self.get_balance(user_id, currency)
        return await self.set_balance(user_id, currency, current + amount)

    async def remove_balance(self, user_id: str, currency: str, amount: int) -> bool:
        """减少用户余额"""
        if amount <= 0:
            return False
        if not await self.has_account(user_id):
            await self.create_account(user_id)
        current = await self.get_balance(user_id, currency)
        if current < amount:
            return False
        return await self.set_balance(user_id, currency, current - amount)
