from ..models.placeholder_expansion import PlaceholderExpansion


class PermissionExpansion(PlaceholderExpansion):

    def __init__(self, permission_api):
        self._permission_api = permission_api

    @property
    def identifier(self) -> str:
        return "permission"

    @property
    def author(self) -> str:
        return "Essentials"

    @property
    def version(self) -> str:
        return "1.0.0"

    def can_register(self) -> bool:
        return self._permission_api is not None

    async def on_request(self, params: str) -> str:
        match params:
            case "groups":
                groups = await self._permission_api.get_groups()
                return ", ".join(group.name for group in groups) if groups else "无"

            case _ if params.startswith("has_permission_"):
                parts = params[len("has_permission_"):].split("_", 1)
                if len(parts) == 2:
                    user, permission = parts
                    result = await self._permission_api.has_user_permission(user, permission)
                    return str(result)
                return ""

            case _ if params.startswith("in_group_"):
                parts = params[len("in_group_"):].split("_", 1)
                if len(parts) == 2:
                    user, group = parts
                    user_obj = await self._permission_api.get_user(user)
                    if user_obj:
                        return str(group in user_obj.groups)
                    return "False"
                return ""

            case _:
                return ""
