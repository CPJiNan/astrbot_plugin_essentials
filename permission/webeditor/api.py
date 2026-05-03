from quart import request, jsonify

PLUGIN_NAME = "astrbot_plugin_essentials"


def register_api(context, permission_api):
    async def handle_get_users():
        """获取用户列表"""
        users = await permission_api.get_users()
        return jsonify([user.to_dict() for user in users])

    async def handle_get_user(user_id):
        """获取用户"""
        user = await permission_api.get_user(user_id)
        if not user:
            return jsonify({"error": "未找到指定用户。"}), 404
        return jsonify(user.to_dict())

    async def handle_create_user():
        """创建用户"""
        data = await request.json
        user_id = data.get("user_id")
        if not user_id:
            return jsonify({"error": "用户 ID 不能为空。"}), 400
        success = await permission_api.create_user(user_id)
        if success:
            user = await permission_api.get_user(user_id)
            return jsonify(user.to_dict()), 201
        else:
            return jsonify({"error": "用户已存在。"}), 409

    async def handle_delete_user(user_id):
        """删除用户"""
        success = await permission_api.delete_user(user_id)
        if success:
            return jsonify({"success": True})
        else:
            return jsonify({"error": "未找到指定用户。"}), 404

    async def handle_get_groups():
        """获取权限组列表"""
        groups = await permission_api.get_groups()
        return jsonify([group.to_dict() for group in groups])

    async def handle_get_group(name):
        """获取权限组"""
        group = await permission_api.get_group(name)
        if not group:
            return jsonify({"error": "未找到指定权限组。"}), 404
        return jsonify(group.to_dict())

    async def handle_create_group():
        """创建权限组"""
        data = await request.json
        name = data.get("name")
        display = data.get("display")
        weight = data.get("weight", 0)
        if not name:
            return jsonify({"error": "权限组编辑名不能为空。"}), 400
        success = await permission_api.create_group(name, display, weight)
        if success:
            group = await permission_api.get_group(name)
            return jsonify(group.to_dict()), 201
        else:
            return jsonify({"error": "权限组已存在。"}), 409

    async def handle_delete_group(name):
        """删除权限组"""
        success = await permission_api.delete_group(name)
        if success:
            return jsonify({"success": True})
        else:
            return jsonify({"error": "未找到指定权限组。"}), 404

    async def handle_update_group(name):
        """更新权限组"""
        data = await request.json
        display = data.get("display")
        weight = data.get("weight")
        success = await permission_api.update_group(name, display, weight)
        if success:
            group = await permission_api.get_group(name)
            return jsonify(group.to_dict())
        else:
            return jsonify({"error": "未找到指定权限组。"}), 404

    async def handle_get_user_permissions(user_id):
        """获取用户权限列表"""
        permissions = await permission_api.get_user_permissions(user_id)
        return jsonify([permission.to_dict() for permission in permissions])

    async def handle_add_user_permission(user_id):
        """新增用户权限"""
        data = await request.json
        node = data.get("node")
        value = data.get("value", True)
        priority = data.get("priority", 0)
        source = data.get("source") or "user"
        expiry = data.get("expiry")
        session = data.get("session")
        if not node:
            return jsonify({"error": "权限不能为空。"}), 400
        success = await permission_api.add_user_permission(user_id, node, value, priority, source, expiry, session)
        if success:
            return jsonify({"success": True}), 201
        else:
            return jsonify({"error": "未找到指定用户或新增用户权限失败。"}), 400

    async def handle_remove_user_permission(user_id, node):
        """移除用户权限"""
        data = await request.json or {}
        session = data.get("session")
        success = await permission_api.remove_user_permission(user_id, node, session)
        if success:
            return jsonify({"success": True})
        else:
            return jsonify({"error": "未找到指定权限。"}), 404

    async def handle_get_group_permissions(name):
        """获取权限组权限列表"""
        permissions = await permission_api.get_group_permissions(name)
        return jsonify([permission.to_dict() for permission in permissions])

    async def handle_add_group_permission(name):
        """新增权限组权限"""
        data = await request.json
        node = data.get("node")
        value = data.get("value", True)
        priority = data.get("priority", 0)
        source = data.get("source") or "group"
        expiry = data.get("expiry")
        session = data.get("session")
        if not node:
            return jsonify({"error": "权限不能为空。"}), 400
        success = await permission_api.add_group_permission(name, node, value, priority, source, expiry, session)
        if success:
            return jsonify({"success": True}), 201
        else:
            return jsonify({"error": "未找到指定权限组或新增权限组权限失败。"}), 400

    async def handle_remove_group_permission(name, node):
        """移除权限组权限"""
        data = await request.json or {}
        session = data.get("session")
        success = await permission_api.remove_group_permission(name, node, session)
        if success:
            return jsonify({"success": True})
        else:
            return jsonify({"error": "未找到指定权限。"}), 404

    async def handle_add_user_to_group(user_id, group_name):
        """新增用户权限组"""
        success = await permission_api.add_user_to_group(user_id, group_name)
        if success:
            return jsonify({"success": True}), 201
        else:
            return jsonify({"error": "未找到指定用户或权限组。"}), 400

    async def handle_remove_user_from_group(user_id, group_name):
        """移除用户权限组"""
        success = await permission_api.remove_user_from_group(user_id, group_name)
        if success:
            return jsonify({"success": True})
        else:
            return jsonify({"error": "未找到指定用户或权限组。"}), 404

    async def handle_add_group_parent(name, parent):
        """为权限组新增父权限组"""
        success = await permission_api.add_group_parent(name, parent)
        if success:
            return jsonify({"success": True}), 201
        else:
            return jsonify({"error": "未找到指定权限组或存在循环继承。"}), 400

    async def handle_remove_group_parent(name, parent):
        """从权限组移除父权限组"""
        success = await permission_api.remove_group_parent(name, parent)
        if success:
            return jsonify({"success": True})
        else:
            return jsonify({"error": "未找到指定父权限组。"}), 404

    routes = [
        (f"/{PLUGIN_NAME}/users", handle_get_users, ["GET"], "获取用户列表"),
        (f"/{PLUGIN_NAME}/users/<user_id>", handle_get_user, ["GET"], "获取用户"),
        (f"/{PLUGIN_NAME}/users", handle_create_user, ["POST"], "创建用户"),
        (f"/{PLUGIN_NAME}/users/<user_id>/delete", handle_delete_user, ["POST"], "删除用户"),
        (f"/{PLUGIN_NAME}/groups", handle_get_groups, ["GET"], "获取权限组列表"),
        (f"/{PLUGIN_NAME}/groups/<name>", handle_get_group, ["GET"], "获取权限组"),
        (f"/{PLUGIN_NAME}/groups", handle_create_group, ["POST"], "创建权限组"),
        (f"/{PLUGIN_NAME}/groups/<name>/delete", handle_delete_group, ["POST"], "删除权限组"),
        (f"/{PLUGIN_NAME}/groups/<name>/update", handle_update_group, ["POST"], "更新权限组"),
        (f"/{PLUGIN_NAME}/users/<user_id>/permissions", handle_get_user_permissions, ["GET"], "获取用户权限列表"),
        (f"/{PLUGIN_NAME}/users/<user_id>/permissions", handle_add_user_permission, ["POST"], "新增用户权限"),
        (f"/{PLUGIN_NAME}/users/<user_id>/permissions/<node>/delete", handle_remove_user_permission, ["POST"],
         "移除用户权限"),
        (f"/{PLUGIN_NAME}/groups/<name>/permissions", handle_get_group_permissions, ["GET"], "获取权限组权限列表"),
        (f"/{PLUGIN_NAME}/groups/<name>/permissions", handle_add_group_permission, ["POST"], "新增权限组权限"),
        (f"/{PLUGIN_NAME}/groups/<name>/permissions/<node>/delete", handle_remove_group_permission, ["POST"],
         "移除权限组权限"),
        (f"/{PLUGIN_NAME}/users/<user_id>/groups/<group_name>", handle_add_user_to_group, ["POST"], "新增用户权限组"),
        (f"/{PLUGIN_NAME}/users/<user_id>/groups/<group_name>/delete", handle_remove_user_from_group, ["POST"],
         "移除用户权限组"),
        (f"/{PLUGIN_NAME}/groups/<name>/parents/<parent>", handle_add_group_parent, ["POST"], "新增父权限组"),
        (f"/{PLUGIN_NAME}/groups/<name>/parents/<parent>/delete", handle_remove_group_parent, ["POST"], "移除父权限组"),
    ]

    for route, handler, methods, desc in routes:
        context.register_web_api(route, handler, methods, desc)
