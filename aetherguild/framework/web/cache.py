import aioredis
from dynaconf import settings
import logging

log = logging.getLogger(__name__)


class Cache(object):
    def __init__(self):
        self._pool = None

    async def connect(self, loop):
        self._pool = await aioredis.create_pool(
            (settings.REDIS['host'], settings.REDIS['port']),
            minsize=settings.REDIS['pool_min'],
            maxsize=settings.REDIS['pool_max'],
            db=settings.REDIS['database'],
            encoding='utf-8',
            loop=loop)

    async def set(self, key, value):
        with await self._pool as conn:
            await conn.set(key, value)

    async def get(self, key):
        with await self._pool as conn:
            return await conn.get(key)

    async def delete(self, key):
        with await self._pool as conn:
            await conn.delete(key)

    async def close(self):
        self._pool.close()
        await self._pool.wait_closed()


async def init_cache(app):
    app['cache'] = Cache()
    await app['cache'].connect(app.loop)
    log.info("Cache: Redis connected to %s:%d", settings.REDIS['host'], settings.REDIS['port'])


async def close_cache(app):
    if 'cache' in app and app['cache']:
        await app['cache'].close()
        log.info("Cache: Redis connection closed")
