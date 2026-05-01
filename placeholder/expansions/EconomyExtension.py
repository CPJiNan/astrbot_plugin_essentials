from ..models.placeholder_expansion import PlaceholderExpansion


class EconomyExpansion(PlaceholderExpansion):

    def __init__(self, economy_api):
        self._economy_api = economy_api

    @property
    def identifier(self) -> str:
        return "economy"

    @property
    def author(self) -> str:
        return "Essentials"

    @property
    def version(self) -> str:
        return "1.0.0"

    def can_register(self) -> bool:
        return self._economy_api is not None

    async def on_request(self, params: str) -> str:
        match params:
            case _ if params.startswith("balance_"):
                parts = params[len("balance_"):].split("_", 1)
                if len(parts) == 2:
                    user_id, currency = parts
                    if await self._economy_api.has_account(user_id):
                        balance = await self._economy_api.get_balance(user_id, currency)
                        return str(balance)
                    return "0"
                return ""

            case _ if params.startswith("has_account_"):
                user_id = params[len("has_account_"):]
                return str(await self._economy_api.has_account(user_id))

            case _:
                return ""
