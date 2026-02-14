"""Redis cache for high-performance caching"""
import redis.asyncio as redis
import json
import pickle
from datetime import datetime
from typing import Optional, Any
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Global Redis client
_redis_client: Optional[redis.Redis] = None


async def get_redis() -> redis.Redis:
    """Get or create Redis connection"""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
    return _redis_client


async def cache_set(key: str, value: Any, ttl: int = 300) -> bool:
    """Cache any Python object with TTL (seconds)"""
    try:
        r = await get_redis()
        # Serialize with pickle for complex objects
        serialized = pickle.dumps(value)
        await r.setex(f"citadel:{key}", ttl, serialized)
        return True
    except Exception as e:
        print(f"[Redis Cache Error] {e}")
        return False


async def cache_get(key: str) -> Optional[Any]:
    """Retrieve cached object"""
    try:
        r = await get_redis()
        data = await r.get(f"citadel:{key}")
        if data:
            return pickle.loads(data)
        return None
    except Exception as e:
        print(f"[Redis Cache Error] {e}")
        return None


async def cache_delete(key: str) -> bool:
    """Delete cached key"""
    try:
        r = await get_redis()
        await r.delete(f"citadel:{key}")
        return True
    except Exception:
        return False


async def cache_exists(key: str) -> bool:
    """Check if key exists in cache"""
    try:
        r = await get_redis()
        return await r.exists(f"citadel:{key}") > 0
    except Exception:
        return False


class CacheStats:
    """Cache performance monitoring"""
    
    @staticmethod
    async def get_stats():
        """Get Redis statistics"""
        try:
            r = await get_redis()
            info = await r.info()
            return {
                "used_memory_human": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients"),
                "total_keys": await r.dbsize(),
                "hit_rate": info.get("keyspace_hits", 0) / max(1, info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0)),
            }
        except Exception as e:
            return {"error": str(e)}
