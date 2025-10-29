# basit, güvenli bir redis lock implementasyonu
import asyncio
import uuid
from typing import Optional
import redis.asyncio as aioredis

LOCK_RELEASE_SCRIPT = """
if redis.call('get', KEYS[1]) == ARGV[1] then
    return redis.call('del', KEYS[1])
else
    return 0
end
"""

class RedisDLock:
    def __init__(self, redis_client: aioredis.Redis, name: str, ttl_ms: int = 10000):
        self.redis = redis_client
        self.name = name
        self.ttl_ms = ttl_ms
        self.token: Optional[str] = None

    async def acquire(self) -> bool:
        token = str(uuid.uuid4())
        ok = await self.redis.set(self.name, token, nx=True, px=self.ttl_ms)
        if ok:
            self.token = token
            return True
        return False

    async def release(self) -> bool:
        if not self.token:
            return False
        try:
            res = await self.redis.eval(LOCK_RELEASE_SCRIPT, 1, self.name, self.token)
            return res == 1
        finally:
            self.token = None

    async def extend(self, extra_ms: int) -> bool:
        # basit extend: check token and set px via Lua script might be safer
        cur = await self.redis.get(self.name)
        if cur and cur.decode() == self.token:
            await self.redis.pexpire(self.name, extra_ms)
            return True
        return False
