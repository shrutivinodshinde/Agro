# backend/database/redis_cache.py
import json
import redis.asyncio as aioredis    # FIXED: was "import aioredis"
from backend.config import get_settings

settings = get_settings()
_redis = None

async def get_redis():
    global _redis
    if _redis is None:
        _redis = await aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
    return _redis

class RedisCache:
    @staticmethod
    async def get(key: str):
        try:
            r = await get_redis()
            val = await r.get(f"agriguard:{key}")
            return json.loads(val) if val else None
        except Exception:
            return None   # cache miss, not a crash

    @staticmethod
    async def set(key: str, value: dict, ttl: int = 3600):
        try:
            r = await get_redis()
            await r.setex(
                f"agriguard:{key}",
                ttl,
                json.dumps(value, default=str)
            )
        except Exception:
            pass   # cache failure shouldn't crash the API