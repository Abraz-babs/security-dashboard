"""Backend Data Cache — Prevents redundant external API calls.
Caches results for configurable TTL. Used by dashboard and broadcast.
"""
import time
from typing import Any, Optional

_cache: dict[str, dict] = {}
DEFAULT_TTL = 90  # seconds


def get(key: str) -> Optional[Any]:
    """Get cached value if not expired."""
    entry = _cache.get(key)
    if entry and time.time() - entry["ts"] < entry["ttl"]:
        return entry["data"]
    return None


def set(key: str, data: Any, ttl: int = DEFAULT_TTL):
    """Store value in cache with TTL."""
    _cache[key] = {"data": data, "ts": time.time(), "ttl": ttl}


def invalidate(pattern: str = None):
    """Invalidate cache entries matching pattern, or all if None."""
    if pattern is None:
        _cache.clear()
        return
    keys_to_delete = [k for k in _cache if pattern in k]
    for k in keys_to_delete:
        del _cache[k]
