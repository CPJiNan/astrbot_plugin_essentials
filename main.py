from typing import Optional

from astrbot.api import logger, AstrBotConfig
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.message_components import Plain
from astrbot.api.star import Context, Star

from .permission import PermissionAPI
from .placeholder import PlaceholderAPI, PermissionExpansion
from .webeditor import WebEditor


class EssentialsPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config
        self.permission_api: Optional[PermissionAPI] = None
        self.placeholder_api: Optional[PlaceholderAPI] = None
        self.web_editor: Optional[WebEditor] = None

        if self.config.get("permission", {}).get("enabled", True):
            self.permission_api = PermissionAPI(self, self.config)
            self.context.essentials_permission_api = self.permission_api

        if self.config.get("placeholder", {}).get("enabled", True):
            self.placeholder_api = PlaceholderAPI(self.config)
            self.context.essentials_placeholder_api = self.placeholder_api

    async def initialize(self):
        if self.permission_api:
            await self.permission_api.initialize()

        if self.placeholder_api:
            await self.placeholder_api.initialize()
            if self.permission_api:
                await self.placeholder_api.register(PermissionExpansion(self.permission_api))

        if self.config.get("webeditor", {}).get("enabled", True) and self.permission_api:
            self.web_editor = WebEditor(
                self.permission_api,
                host=self.config.get("webeditor", {}).get("host", "127.0.0.1"),
                port=self.config.get("webeditor", {}).get("port", 25560)
            )

        logger.info("插件加载成功。")

    async def terminate(self):
        if self.permission_api:
            await self.permission_api.terminate()
        if self.placeholder_api:
            await self.placeholder_api.terminate()
        if self.web_editor:
            await self.web_editor.stop()
        logger.info("插件卸载成功。")

    @filter.on_decorating_result()
    async def on_decorating_result(self, event: AstrMessageEvent):
        """回复消息前事件"""
        result = event.get_result()
        if not result:
            return

        if self.placeholder_api and self.config.get("placeholder", {}).get("parse_message", True):
            for component in result.chain:
                if isinstance(component, Plain):
                    component.text = await self.placeholder_api.set_placeholders(component.text)

    @filter.command_group("permission", alias={'perm', '权限管理'})
    def permission(self):
        """权限管理命令组"""
        pass

    @permission.group("user", alias={'u', '用户'})
    def user(self):
        """用户命令组"""
        pass

    @user.command("info", alias={'i', '信息'})
    async def user_info(self, event: AstrMessageEvent, user_id: str):
        """获取用户信息"""
        if not self.permission_api:
            yield event.plain_result("权限模块未启用。")
            return
        if not event.is_admin() and not await self.permission_api.has_user_permission(event.get_sender_id(),
                                                                                      "essentials.permission.user.info",
                                                                                      event.session_id):
            yield event.plain_result("无使用当前命令的权限。")
            return
        user = await self.permission_api.get_user(user_id)
        if not user:
            yield event.plain_result(f"未找到用户 {user_id}。")
            return
        permissions = await self.permission_api.get_user_permissions(user_id)
        permissions_str = ", ".join(
            f"{'+' if permission.value else '-'}{permission.node}" for permission in permissions
        ) if permissions else "无"
        groups_str = ", ".join(user.groups) if user.groups else "无"
        yield event.plain_result(f"用户 {user_id}：\n"
                                 f"权限组：{groups_str}\n"
                                 f"权限列表：{permissions_str}")

    @user.group("permission", alias={'p', 'perm', '权限'})
    def user_permission(self):
        """用户权限命令组"""
        pass

    @user_permission.command("has", alias={'h', '检查'})
    async def user_permission_has(self, event: AstrMessageEvent, user_id: str, node: str):
        """检查用户权限"""
        if not self.permission_api:
            yield event.plain_result("权限模块未启用。")
            return
        if not event.is_admin() and not await self.permission_api.has_user_permission(event.get_sender_id(),
                                                                                      "essentials.permission.user.permission.has",
                                                                                      event.session_id):
            yield event.plain_result("无使用当前命令的权限。")
            return
        result = await self.permission_api.has_user_permission(user_id, node, event.session_id)
        yield event.plain_result(f"用户 {user_id} {'有' if result else '无'}权限 {node}。")

    @user_permission.command("add", alias={'a', '新增'})
    async def user_permission_add(self, event: AstrMessageEvent, user_id: str, node: str):
        """新增用户权限"""
        if not self.permission_api:
            yield event.plain_result("权限模块未启用。")
            return
        if not event.is_admin() and not await self.permission_api.has_user_permission(event.get_sender_id(),
                                                                                      "essentials.permission.user.permission.add",
                                                                                      event.session_id):
            yield event.plain_result("无使用当前命令的权限。")
            return
        result = await self.permission_api.add_user_permission(user_id, node)
        yield event.plain_result(f"新增用户权限{'成功' if result else '失败'}。")

    @user_permission.command("remove", alias={'r', '移除'})
    async def user_permission_remove(self, event: AstrMessageEvent, user_id: str, node: str):
        """移除用户权限"""
        if not self.permission_api:
            yield event.plain_result("权限模块未启用。")
            return
        if not event.is_admin() and not await self.permission_api.has_user_permission(event.get_sender_id(),
                                                                                      "essentials.permission.user.permission.remove",
                                                                                      event.session_id):
            yield event.plain_result("无使用当前命令的权限。")
            return
        result = await self.permission_api.remove_user_permission(user_id, node)
        yield event.plain_result(f"移除用户权限{'成功' if result else '失败'}。")

    @user.group("group", alias={'g', '权限组'})
    def user_group(self):
        """用户权限组命令组"""
        pass

    @user_group.command("add", alias={'a', '新增'})
    async def user_group_add(self, event: AstrMessageEvent, user_id: str, group_name: str):
        """新增用户权限组"""
        if not self.permission_api:
            yield event.plain_result("权限模块未启用。")
            return
        if not event.is_admin() and not await self.permission_api.has_user_permission(event.get_sender_id(),
                                                                                      "essentials.permission.user.group.add",
                                                                                      event.session_id):
            yield event.plain_result("无使用当前命令的权限。")
            return
        result = await self.permission_api.add_user_to_group(user_id, group_name)
        yield event.plain_result(f"新增用户权限组{'成功' if result else '失败'}。")

    @user_group.command("remove", alias={'r', '移除'})
    async def user_group_remove(self, event: AstrMessageEvent, user_id: str, group_name: str):
        """移除用户权限组"""
        if not self.permission_api:
            yield event.plain_result("权限模块未启用。")
            return
        if not event.is_admin() and not await self.permission_api.has_user_permission(event.get_sender_id(),
                                                                                      "essentials.permission.user.group.remove",
                                                                                      event.session_id):
            yield event.plain_result("无使用当前命令的权限。")
            return
        result = await self.permission_api.remove_user_from_group(user_id, group_name)
        yield event.plain_result(f"移除用户权限组{'成功' if result else '失败'}。")

    @permission.group("group", alias={'g', '权限组'})
    def group(self):
        """权限组命令组"""
        pass

    @group.command("list", alias={'l', '列表'})
    async def group_list(self, event: AstrMessageEvent):
        """获取权限组列表"""
        if not self.permission_api:
            yield event.plain_result("权限模块未启用。")
            return
        if not event.is_admin() and not await self.permission_api.has_user_permission(event.get_sender_id(),
                                                                                      "essentials.permission.group.list",
                                                                                      event.session_id):
            yield event.plain_result("无使用当前命令的权限。")
            return
        groups = await self.permission_api.get_groups()
        if not groups:
            yield event.plain_result("暂无权限组。")
            return
        group_list = ", ".join(f"{group.name}({group.display})" if group.display else group.name for group in groups)
        yield event.plain_result(f"权限组列表：\n{group_list}")

    @group.command("info", alias={'i', '信息'})
    async def group_info(self, event: AstrMessageEvent, group_name: str):
        """获取权限组信息"""
        if not self.permission_api:
            yield event.plain_result("权限模块未启用。")
            return
        if not event.is_admin() and not await self.permission_api.has_user_permission(event.get_sender_id(),
                                                                                      "essentials.permission.group.info",
                                                                                      event.session_id):
            yield event.plain_result("无使用当前命令的权限。")
            return
        group = await self.permission_api.get_group(group_name)
        if not group:
            yield event.plain_result(f"未找到权限组 {group_name}。")
            return
        permissions_str = ", ".join(
            f"{'+' if permission.value else '-'}{permission.node}" for permission in group.permissions
        ) if group.permissions else "无"
        yield event.plain_result(f"权限组 {group_name}：\n"
                                 f"展示名：{group.display or '无'}\n"
                                 f"权重：{group.weight}\n"
                                 f"父权限组：{', '.join(group.parents) if group.parents else '无'}\n"
                                 f"权限列表：{permissions_str}")

    @group.command("create", alias={'c', '创建'})
    async def group_create(self, event: AstrMessageEvent, group_name: str):
        """创建权限组"""
        if not self.permission_api:
            yield event.plain_result("权限模块未启用。")
            return
        if not event.is_admin() and not await self.permission_api.has_user_permission(event.get_sender_id(),
                                                                                      "essentials.permission.group.create",
                                                                                      event.session_id):
            yield event.plain_result("无使用当前命令的权限。")
            return
        result = await self.permission_api.create_group(group_name)
        yield event.plain_result(f"创建权限组{'成功' if result else '失败'}。")

    @group.command("delete", alias={'d', '删除'})
    async def group_delete(self, event: AstrMessageEvent, group_name: str):
        """删除权限组"""
        if not self.permission_api:
            yield event.plain_result("权限模块未启用。")
            return
        if not event.is_admin() and not await self.permission_api.has_user_permission(event.get_sender_id(),
                                                                                      "essentials.permission.group.delete",
                                                                                      event.session_id):
            yield event.plain_result("无使用当前命令的权限。")
            return
        result = await self.permission_api.delete_group(group_name)
        yield event.plain_result(f"删除权限组{'成功' if result else '失败'}。")

    @group.group("permission", alias={'p', 'perm', '权限'})
    def group_permission(self):
        """权限组权限命令组"""
        pass

    @group_permission.command("add", alias={'a', '新增'})
    async def group_permission_add(self, event: AstrMessageEvent, group_name: str, node: str):
        """新增权限组权限"""
        if not self.permission_api:
            yield event.plain_result("权限模块未启用。")
            return
        if not event.is_admin() and not await self.permission_api.has_user_permission(event.get_sender_id(),
                                                                                      "essentials.permission.group.permission.add",
                                                                                      event.session_id):
            yield event.plain_result("无使用当前命令的权限。")
            return
        result = await self.permission_api.add_group_permission(group_name, node)
        yield event.plain_result(f"新增权限组权限{'成功' if result else '失败'}。")

    @group_permission.command("remove", alias={'r', '移除'})
    async def group_permission_remove(self, event: AstrMessageEvent, group_name: str, node: str):
        """移除权限组权限"""
        if not self.permission_api:
            yield event.plain_result("权限模块未启用。")
            return
        if not event.is_admin() and not await self.permission_api.has_user_permission(event.get_sender_id(),
                                                                                      "essentials.permission.group.permission.remove",
                                                                                      event.session_id):
            yield event.plain_result("无使用当前命令的权限。")
            return
        result = await self.permission_api.remove_group_permission(group_name, node)
        yield event.plain_result(f"移除权限组权限{'成功' if result else '失败'}。")

    @group.group("parent", alias={'父权限组'})
    def group_parent(self):
        """父权限组命令组"""
        pass

    @group_parent.command("add", alias={'a', '新增'})
    async def group_parent_add(self, event: AstrMessageEvent, group_name: str, parent: str):
        """为权限组新增父权限组"""
        if not self.permission_api:
            yield event.plain_result("权限模块未启用。")
            return
        if not event.is_admin() and not await self.permission_api.has_user_permission(event.get_sender_id(),
                                                                                      "essentials.permission.group.parent.add",
                                                                                      event.session_id):
            yield event.plain_result("无使用当前命令的权限。")
            return
        result = await self.permission_api.add_group_parent(group_name, parent)
        yield event.plain_result(f"为权限组新增父权限组{'成功' if result else '失败'}。")

    @group_parent.command("remove", alias={'r', '移除'})
    async def group_parent_remove(self, event: AstrMessageEvent, group_name: str, parent: str):
        """从权限组移除父权限组"""
        if not self.permission_api:
            yield event.plain_result("权限模块未启用。")
            return
        if not event.is_admin() and not await self.permission_api.has_user_permission(event.get_sender_id(),
                                                                                      "essentials.permission.group.parent.remove",
                                                                                      event.session_id):
            yield event.plain_result("无使用当前命令的权限。")
            return
        result = await self.permission_api.remove_group_parent(group_name, parent)
        yield event.plain_result(f"从权限组移除父权限组{'成功' if result else '失败'}。")

    @permission.group("editor", alias={'e', '编辑器'})
    def editor(self):
        """网页编辑器命令组"""
        pass

    @editor.command("start", alias={'启动'})
    async def editor_start(self, event: AstrMessageEvent):
        """启动网页编辑器"""
        if not self.permission_api:
            yield event.plain_result("权限模块未启用。")
            return
        if not event.is_admin() and not await self.permission_api.has_user_permission(event.get_sender_id(),
                                                                                      "essentials.permission.editor.start",
                                                                                      event.session_id):
            yield event.plain_result("无使用当前命令的权限。")
            return
        if not self.web_editor:
            yield event.plain_result("网页编辑器未启用。")
            return
        try:
            url, token = await self.web_editor.start()
            yield event.plain_result(
                f"网页编辑器已在 {url} 上启动。\n"
                f"访问令牌：{token}"
            )
        except Exception as e:
            logger.error(f"启动网页编辑器失败：{e}。")
            yield event.plain_result(f"启动网页编辑器失败：{e}。")

    @editor.command("stop", alias={'关闭'})
    async def editor_stop(self, event: AstrMessageEvent):
        """关闭网页编辑器"""
        if not self.permission_api:
            yield event.plain_result("权限模块未启用。")
            return
        if not event.is_admin() and not await self.permission_api.has_user_permission(event.get_sender_id(),
                                                                                      "essentials.permission.editor.stop",
                                                                                      event.session_id):
            yield event.plain_result("无使用当前命令的权限。")
            return
        if not self.web_editor:
            yield event.plain_result("网页编辑器未启用。")
            return
        is_running = await self.web_editor.is_running()
        if not is_running:
            yield event.plain_result("网页编辑器未运行。")
            return
        try:
            await self.web_editor.stop()
            yield event.plain_result("网页编辑器已关闭。")
        except Exception as e:
            logger.error(f"关闭网页编辑器失败：{e}。")
            yield event.plain_result(f"关闭网页编辑器失败：{e}。")

    @editor.command("status", alias={'状态'})
    async def editor_status(self, event: AstrMessageEvent):
        """查看网页编辑器状态"""
        if not self.permission_api:
            yield event.plain_result("权限模块未启用。")
            return
        if not event.is_admin() and not await self.permission_api.has_user_permission(event.get_sender_id(),
                                                                                      "essentials.permission.editor.status",
                                                                                      event.session_id):
            yield event.plain_result("无使用当前命令的权限。")
            return
        if not self.web_editor:
            yield event.plain_result("网页编辑器未启用。")
            return
        is_running = await self.web_editor.is_running()
        if is_running:
            host, port = await self.web_editor.get_address()
            yield event.plain_result(f"网页编辑器已在 http://{host}:{port} 上运行。")
        else:
            yield event.plain_result("网页编辑器已关闭。使用 /permission editor start 开启。")

    @filter.command_group("placeholder", alias={'占位符'})
    def placeholder(self):
        """占位符命令组"""
        pass

    @placeholder.command("parse", alias={'p', '解析'})
    async def placeholder_parse(self, event: AstrMessageEvent, text: str):
        """解析文本中的占位符"""
        if not self.placeholder_api:
            yield event.plain_result("占位符模块未启用。")
            return
        if not self.permission_api:
            yield event.plain_result("权限模块未启用。")
            return
        if not event.is_admin() and not await self.permission_api.has_user_permission(event.get_sender_id(),
                                                                                      "essentials.placeholder.parse",
                                                                                      event.session_id):
            yield event.plain_result("无使用当前命令的权限。")
            return
        result = await self.placeholder_api.set_placeholders(text)
        yield event.plain_result(result)

    @placeholder.command("list", alias={'l', '列表'})
    async def placeholder_list(self, event: AstrMessageEvent):
        """获取占位符扩展列表"""
        if not self.placeholder_api:
            yield event.plain_result("占位符模块未启用。")
            return
        if not self.permission_api:
            yield event.plain_result("权限模块未启用。")
            return
        if not event.is_admin() and not await self.permission_api.has_user_permission(event.get_sender_id(),
                                                                                      "essentials.placeholder.list",
                                                                                      event.session_id):
            yield event.plain_result("无使用当前命令的权限。")
            return
        expansions = await self.placeholder_api.get_expansions()
        if not expansions:
            yield event.plain_result("暂无占位符扩展。")
            return
        expansion_list = ", ".join(f"{expansion.identifier}" for expansion in expansions)
        yield event.plain_result(f"占位符扩展列表：\n{expansion_list}")

    @placeholder.command("info", alias={'i', '信息'})
    async def placeholder_info(self, event: AstrMessageEvent, identifier: str):
        """获取占位符扩展信息"""
        if not self.placeholder_api:
            yield event.plain_result("占位符模块未启用。")
            return
        if not self.permission_api:
            yield event.plain_result("权限模块未启用。")
            return
        if not event.is_admin() and not await self.permission_api.has_user_permission(event.get_sender_id(),
                                                                                      "essentials.placeholder.info",
                                                                                      event.session_id):
            yield event.plain_result("无使用当前命令的权限。")
            return
        expansion = await self.placeholder_api.get_expansion(identifier)
        if not expansion:
            yield event.plain_result(f"未找到占位符扩展 {identifier}。")
            return
        yield event.plain_result(
            f"标识符：{expansion.identifier}\n"
            f"作者：{expansion.author}\n"
            f"版本：{expansion.version}\n"
        )
