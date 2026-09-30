"""JSON cache: Upstash Redis if configured, else in-process TTL dict. Never raises."""
import json
import logging
import time

from .config import settings

log = logging.getLogger("accessinav.cache")

_redis = None
if settings.upstash_redis_rest_url and settings.upstash_redis_rest_token:
    try:
        from upstash_redis import Redis

        _redis = Redis(url=settings.upstash_redis_rest_url, token=settings.upstash_redis_rest_token)
    except Exception as e:
        log.warning("Redis init failed, using memory cache: %s", e)

_mem: dict[str, tuple[float, str]] = {}


def cache_get(key: str):
    try:
        if _redis:
            raw = _redis.get(key)
            return json.loads(raw) if isinstance(raw, str) else raw
        hit = _mem.get(key)
        if hit and hit[0] > time.time():
            return json.loads(hit[1])
    except Exception as e:
        log.warning("cache get failed: %s", e)
    return None


def cache_set(key: str, value, ttl: int = 30) -> None:
    try:
        if _redis:
            _redis.set(key, json.dumps(value), ex=ttl)
        else:
            if len(_mem) > 500:
                _mem.clear()
            _mem[key] = (time.time() + ttl, json.dumps(value))
    except Exception as e:
        log.warning("cache set failed: %s", e)


def backend_name() -> str:
    return "redis" if _redis else "memory"
