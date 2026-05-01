from dataclasses import dataclass
from typing import Dict

from .account import Account


@dataclass
class EconomyData:
    accounts: Dict[str, Account] = None  # 账户数据

    def __post_init__(self):
        if self.accounts is None:
            self.accounts = {}

    def to_dict(self) -> dict:
        return {
            'accounts': {user_id: account.to_dict() for user_id, account in self.accounts.items()}
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'EconomyData':
        accounts = {user_id: Account.from_dict(account_data) for user_id, account_data in
                    data.get('accounts', {}).items()}
        return cls(accounts=accounts)
