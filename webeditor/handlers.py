import hmac
from pathlib import Path

from aiohttp import web


@web.middleware
async def token_auth_middleware(request: web.Request, handler):
    """访问令牌验证中间件"""
    path = request.path
    if (path.startswith('/static/') or
            path == '/' or
            path == '/api/auth/verify'):
        return await handler(request)
    token = request.app.get('auth_token')
    if not token:
        return web.json_response({'error': '服务器未配置访问令牌。'}, status=500)
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        input_token = auth_header[7:]
    else:
        return web.json_response({'error': '缺少访问令牌。'}, status=401)
    if not hmac.compare_digest(input_token, token):
        return web.json_response({'error': '访问令牌无效。'}, status=401)
    return await handler(request)


def setup_routes(app: web.Application):
    """注册 API 路由"""
    static_path = Path(__file__).parent / 'static'

    app.middlewares.append(token_auth_middleware)

    app.router.add_static('/static', static_path)
    app.router.add_get('/', handle_index)

    app.router.add_post('/api/auth/verify', handle_verify_token)

    app.router.add_get('/api/users/{user_id}', handle_get_user)
    app.router.add_get('/api/users', handle_get_users)
    app.router.add_post('/api/users', handle_create_user)
    app.router.add_delete('/api/users/{user_id}', handle_delete_user)

    app.router.add_get('/api/groups/{name}', handle_get_group)
    app.router.add_get('/api/groups', handle_get_groups)
    app.router.add_post('/api/groups', handle_create_group)
    app.router.add_delete('/api/groups/{name}', handle_delete_group)
    app.router.add_put('/api/groups/{name}', handle_update_group)

    app.router.add_get('/api/users/{user_id}/permissions', handle_get_user_permissions)
    app.router.add_post('/api/users/{user_id}/permissions', handle_add_user_permission)
    app.router.add_delete('/api/users/{user_id}/permissions/{node}', handle_remove_user_permission)

    app.router.add_get('/api/groups/{name}/permissions', handle_get_group_permissions)
    app.router.add_post('/api/groups/{name}/permissions', handle_add_group_permission)
    app.router.add_delete('/api/groups/{name}/permissions/{node}', handle_remove_group_permission)

    app.router.add_post('/api/users/{user_id}/groups/{group_name}', handle_add_user_to_group)
    app.router.add_delete('/api/users/{user_id}/groups/{group_name}', handle_remove_user_from_group)

    app.router.add_post('/api/groups/{name}/parents/{parent}', handle_add_group_parent)
    app.router.add_delete('/api/groups/{name}/parents/{parent}', handle_remove_group_parent)


def get_permission_api(request: web.Request):
    """获取权限接口"""
    return request.app['permission_api']


async def handle_index(request: web.Request) -> web.Response:
    """获取主页面"""
    index_path = request.app['index_path']
    return web.FileResponse(index_path)


async def handle_verify_token(request: web.Request) -> web.Response:
    """验证访问令牌"""
    token = request.app.get('auth_token')
    if not token:
        return web.json_response({'valid': False, 'error': '服务器未配置访问令牌。'}, status=500)
    try:
        data = await request.json()
    except Exception:
        return web.json_response({'valid': False, 'error': '请求格式错误。'}, status=400)
    input_token = data.get('token', '')
    if hmac.compare_digest(input_token, token):
        return web.json_response({'valid': True})
    else:
        return web.json_response({'valid': False, 'error': '访问令牌无效。'}, status=401)


async def handle_get_user(request: web.Request) -> web.Response:
    """获取用户"""
    api = get_permission_api(request)
    user_id = request.match_info['user_id']
    user = await api.get_user(user_id)
    if not user:
        return web.json_response({'error': '未找到指定用户。'}, status=404)
    return web.json_response(user.to_dict())


async def handle_get_users(request: web.Request) -> web.Response:
    """获取用户列表"""
    api = get_permission_api(request)
    users = await api.get_users()
    return web.json_response([user.to_dict() for user in users])


async def handle_create_user(request: web.Request) -> web.Response:
    """创建用户"""
    api = get_permission_api(request)
    data = await request.json()
    user_id = data.get('user_id')
    if not user_id:
        return web.json_response({'error': '用户 ID 不能为空。'}, status=400)
    success = await api.create_user(user_id)
    if success:
        user = await api.get_user(user_id)
        return web.json_response(user.to_dict(), status=201)
    else:
        return web.json_response({'error': '用户已存在。'}, status=409)


async def handle_delete_user(request: web.Request) -> web.Response:
    """删除用户"""
    api = get_permission_api(request)
    user_id = request.match_info['user_id']
    success = await api.delete_user(user_id)
    if success:
        return web.json_response({'success': True})
    else:
        return web.json_response({'error': '未找到指定用户。'}, status=404)


async def handle_get_group(request: web.Request) -> web.Response:
    """获取权限组"""
    api = get_permission_api(request)
    name = request.match_info['name']
    group = await api.get_group(name)
    if not group:
        return web.json_response({'error': '未找到指定权限组。'}, status=404)
    return web.json_response(group.to_dict())


async def handle_get_groups(request: web.Request) -> web.Response:
    """获取权限组列表"""
    api = get_permission_api(request)
    groups = await api.get_groups()
    return web.json_response([group.to_dict() for group in groups])


async def handle_create_group(request: web.Request) -> web.Response:
    """创建权限组"""
    api = get_permission_api(request)
    data = await request.json()
    name = data.get('name')
    display = data.get('display')
    weight = data.get('weight', 0)
    if not name:
        return web.json_response({'error': '权限组编辑名不能为空。'}, status=400)

    success = await api.create_group(name, display, weight)

    if success:
        group = await api.get_group(name)
        return web.json_response(group.to_dict(), status=201)
    else:
        return web.json_response({'error': '权限组已存在。'}, status=409)


async def handle_delete_group(request: web.Request) -> web.Response:
    """删除权限组"""
    api = get_permission_api(request)
    name = request.match_info['name']
    success = await api.delete_group(name)
    if success:
        return web.json_response({'success': True})
    else:
        return web.json_response({'error': '未找到指定权限组。'}, status=404)


async def handle_update_group(request: web.Request) -> web.Response:
    """更新权限组"""
    api = get_permission_api(request)
    name = request.match_info['name']
    data = await request.json()
    display = data.get('display')
    weight = data.get('weight')
    success = await api.update_group(name, display, weight)
    if success:
        group = await api.get_group(name)
        return web.json_response(group.to_dict())
    else:
        return web.json_response({'error': '未找到指定权限组。'}, status=404)


async def handle_get_user_permissions(request: web.Request) -> web.Response:
    """获取用户权限列表"""
    api = get_permission_api(request)
    user_id = request.match_info['user_id']
    permissions = await api.get_user_permissions(user_id)
    return web.json_response([permission.to_dict() for permission in permissions])


async def handle_add_user_permission(request: web.Request) -> web.Response:
    """新增用户权限"""
    api = get_permission_api(request)
    user_id = request.match_info['user_id']
    data = await request.json()
    node = data.get('node')
    value = data.get('value', True)
    priority = data.get('priority', 0)
    source = data.get('source') or 'user'
    expiry = data.get('expiry')
    session = data.get('session')
    if not node:
        return web.json_response({'error': '权限不能为空。'}, status=400)
    success = await api.add_user_permission(user_id, node, value, priority, source, expiry, session)
    if success:
        return web.json_response({'success': True}, status=201)
    else:
        return web.json_response({'error': '未找到指定用户或新增用户权限失败。'}, status=400)


async def handle_remove_user_permission(request: web.Request) -> web.Response:
    """移除用户权限"""
    api = get_permission_api(request)
    user_id = request.match_info['user_id']
    node = request.match_info['node']
    session = request.query.get('session')
    success = await api.remove_user_permission(user_id, node, session)
    if success:
        return web.json_response({'success': True})
    else:
        return web.json_response({'error': '未找到指定权限。'}, status=404)


async def handle_get_group_permissions(request: web.Request) -> web.Response:
    """获取权限组权限列表"""
    api = get_permission_api(request)
    name = request.match_info['name']
    permissions = await api.get_group_permissions(name)
    return web.json_response([permission.to_dict() for permission in permissions])


async def handle_add_group_permission(request: web.Request) -> web.Response:
    """新增权限组权限"""
    api = get_permission_api(request)
    name = request.match_info['name']
    data = await request.json()
    node = data.get('node')
    value = data.get('value', True)
    priority = data.get('priority', 0)
    source = data.get('source') or 'group'
    expiry = data.get('expiry')
    session = data.get('session')
    if not node:
        return web.json_response({'error': '权限不能为空。'}, status=400)
    success = await api.add_group_permission(name, node, value, priority, source, expiry, session)
    if success:
        return web.json_response({'success': True}, status=201)
    else:
        return web.json_response({'error': '未找到指定权限组或新增权限组权限失败。'}, status=400)


async def handle_remove_group_permission(request: web.Request) -> web.Response:
    """移除权限组权限"""
    api = get_permission_api(request)
    name = request.match_info['name']
    node = request.match_info['node']
    session = request.query.get('session')
    success = await api.remove_group_permission(name, node, session)
    if success:
        return web.json_response({'success': True})
    else:
        return web.json_response({'error': '未找到指定权限。'}, status=404)


async def handle_add_user_to_group(request: web.Request) -> web.Response:
    """新增用户权限组"""
    api = get_permission_api(request)
    user_id = request.match_info['user_id']
    group_name = request.match_info['group_name']

    success = await api.add_user_to_group(user_id, group_name)

    if success:
        return web.json_response({'success': True}, status=201)
    else:
        return web.json_response({'error': '未找到指定用户或权限组。'}, status=400)


async def handle_remove_user_from_group(request: web.Request) -> web.Response:
    """移除用户权限组"""
    api = get_permission_api(request)
    user_id = request.match_info['user_id']
    group_name = request.match_info['group_name']
    success = await api.remove_user_from_group(user_id, group_name)
    if success:
        return web.json_response({'success': True})
    else:
        return web.json_response({'error': '未找到指定用户或权限组。'}, status=404)


async def handle_add_group_parent(request: web.Request) -> web.Response:
    """为权限组新增父权限组"""
    api = get_permission_api(request)
    name = request.match_info['name']
    parent = request.match_info['parent']
    success = await api.add_group_parent(name, parent)
    if success:
        return web.json_response({'success': True}, status=201)
    else:
        return web.json_response({'error': '未找到指定权限组或存在循环继承。'}, status=400)


async def handle_remove_group_parent(request: web.Request) -> web.Response:
    """从权限组移除父权限组"""
    api = get_permission_api(request)
    name = request.match_info['name']
    parent = request.match_info['parent']
    success = await api.remove_group_parent(name, parent)
    if success:
        return web.json_response({'success': True})
    else:
        return web.json_response({'error': '未找到指定父权限组。'}, status=404)
