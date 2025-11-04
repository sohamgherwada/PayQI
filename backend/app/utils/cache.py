from cachetools import TTLCache
from typing import Optional, Any
from app.config import settings
import redis
import json

# In-memory cache fallback
_memory_cache: Optional[TTLCache] = None
_redis_client: Optional[redis.Redis] = None


def init_cache() -> None:
    """Initialize caching system"""
    global _memory_cache, _redis_client

    # Try to connect to Redis if URL is provided
    if settings.REDIS_URL:
        try:
            _redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )
            # Test connection
            _redis_client.ping()
            return
        except Exception:
            pass  # Fall back to in-memory cache

    # Fallback to in-memory cache
    _memory_cache = TTLCache(maxsize=1000, ttl=settings.EXCHANGE_RATE_CACHE_TTL)


def get_cache(key: str) -> Optional[Any]:
    """Get value from cache"""
    if _redis_client:
        try:
            value = _redis_client.get(key)
            return json.loads(value) if value else None
        except Exception:
            return None

    if _memory_cache:
        return _memory_cache.get(key)

    return None


def set_cache(key: str, value: Any, ttl: Optional[int] = None) -> None:
    """Set value in cache"""
    if _redis_client:
        try:
            _redis_client.setex(key, ttl or settings.EXCHANGE_RATE_CACHE_TTL, json.dumps(value))
            return
        except Exception:
            pass

    if _memory_cache:
        _memory_cache[key] = value
