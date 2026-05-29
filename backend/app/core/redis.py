"""Optional Redis client wrapper. Fails closed when Redis is unavailable."""

from app.core.config import settings
from app.core.logging import logger


class RedisClient:
    """Lazy Redis client. All methods are no-ops when Redis is disabled/unavailable."""

    def __init__(self, redis_url: str = ""):
        self._redis_url = redis_url or settings.redis_url
        self._client = None
        self._available: bool | None = None
        self._import_error: str | None = None

    @property
    def available(self) -> bool:
        if self._available is not None:
            return self._available
        if not self._redis_url:
            self._available = False
            return False
        try:
            import redis.asyncio  # type: ignore
            self._client = redis.asyncio.from_url(
                self._redis_url,
                socket_connect_timeout=3,
                socket_timeout=3,
                health_check_interval=30,
                retry_on_timeout=False,
            )
            self._available = True
            logger.info(f"Redis connected: {self._redis_url.split('@')[-1] if '@' in self._redis_url else self._redis_url}")
        except ImportError as e:
            self._import_error = str(e)
            self._available = False
            logger.warning(f"Redis not available (import error): {e}")
        except Exception as e:
            self._available = False
            logger.warning(f"Redis connection failed: {e}")
        return self._available

    async def get(self, key: str) -> bytes | None:
        if not self.available or not self._client:
            return None
        try:
            return await self._client.get(key)
        except Exception:
            self._available = False
            logger.warning("Redis get failed, marking unavailable")
            return None

    async def set(self, key: str, value: bytes, ttl: int = 3600) -> bool:
        if not self.available or not self._client:
            return False
        try:
            await self._client.setex(key, ttl, value)
            return True
        except Exception:
            self._available = False
            logger.warning("Redis set failed, marking unavailable")
            return False

    async def delete(self, key: str) -> int:
        if not self.available or not self._client:
            return 0
        try:
            return await self._client.delete(key)
        except Exception:
            self._available = False
            return 0

    async def ping(self) -> bool:
        if not self.available or not self._client:
            return False
        try:
            return await self._client.ping()
        except Exception:
            self._available = False
            return False


redis_client = RedisClient()
