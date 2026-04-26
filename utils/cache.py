import time
from typing import Optional, Dict, Any


class CacheItem:
    """缓存项"""

    def __init__(self, value: Any, expiry: Optional[int] = None):
        self.value = value
        self.expiry = expiry
        self.created_at = time.time()

    def is_expired(self) -> bool:
        """检查缓存是否过期"""
        if self.expiry is None:
            return False
        return time.time() - self.created_at > self.expiry


class SimpleCache:
    """简单缓存实现"""

    def __init__(self, default_expiry: Optional[int] = None):
        self._cache: Dict[str, CacheItem] = {}
        self.default_expiry = default_expiry

    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        item = self._cache.get(key)
        if not item:
            return None
        if item.is_expired():
            del self._cache[key]
            return None
        return item.value

    def set(self, key: str, value: Any, expiry: Optional[int] = None):
        """设置缓存"""
        self.cleanup()
        self._cache[key] = CacheItem(value, expiry or self.default_expiry)

    def delete(self, key: str):
        """删除缓存"""
        if key in self._cache:
            del self._cache[key]

    def clear(self):
        """清空缓存"""
        self._cache.clear()

    def clear_prefix(self, prefix: str) -> int:
        """清空指定前缀的缓存"""
        keys_to_delete = [key for key in self._cache if key.startswith(prefix)]
        for key in keys_to_delete:
            del self._cache[key]
        return len(keys_to_delete)

    def size(self) -> int:
        """获取缓存大小"""
        return len(self._cache)

    def cleanup(self):
        """清理过期缓存"""
        expired_keys = [key for key, item in self._cache.items() if item.is_expired()]
        for key in expired_keys:
            del self._cache[key]
