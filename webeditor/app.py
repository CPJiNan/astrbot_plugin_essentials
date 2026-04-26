import uuid
from pathlib import Path

from aiohttp import web

from .handlers import setup_routes


class WebEditor:
    """网页权限编辑器服务器"""

    def __init__(self, permission_api, host='127.0.0.1', port=25560):
        self.permission_api = permission_api
        self.host = host
        self.port = port
        self.app = None
        self.runner = None
        self.site = None
        self._running = False
        self._token = None

    async def start(self) -> tuple:
        """启动网页编辑器"""
        self._token = str(uuid.uuid4())
        if not self._running:
            app = web.Application()
            app['index_path'] = Path(__file__).parent / 'static' / 'index.html'
            app['permission_api'] = self.permission_api
            setup_routes(app)
            self.app = app
            self.runner = web.AppRunner(self.app)
            await self.runner.setup()
            self.site = web.TCPSite(self.runner, self.host, self.port)
            await self.site.start()
            self._running = True
        self.app['auth_token'] = self._token
        return f"http://{self.host}:{self.port}", self._token

    async def stop(self):
        """关闭网页编辑器"""
        if not self._running:
            return
        if self.site:
            await self.site.stop()
        if self.runner:
            await self.runner.cleanup()
        self._running = False
        self.app = None
        self.runner = None
        self.site = None

    async def is_running(self) -> bool:
        """检查网页编辑器是否正在运行"""
        return self._running

    async def get_address(self) -> tuple:
        """获取网页编辑器地址"""
        return self.host, self.port
