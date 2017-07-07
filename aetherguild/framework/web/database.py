import logging
from asyncpgsa import create_pool
from dynaconf import settings

log = logging.getLogger(__name__)


async def init_db(app):
    engine = await create_pool(
        database=settings.DATABASE['database'],
        user=settings.DATABASE['username'],
        password=settings.DATABASE['password'],
        host=settings.DATABASE['host'],
        port=settings.DATABASE['port'],
        min_size=settings.DATABASE['pool_min'],
        max_size=settings.DATABASE['pool_max'],
        loop=app.loop)
    app['db'] = engine
    log.info("DB: Connected to %s:%d", settings.DATABASE['host'], settings.DATABASE['port'])

async def close_db(app):
    if app['db']:
        await app['db'].close()
        log.info("DB: Connection closed")
