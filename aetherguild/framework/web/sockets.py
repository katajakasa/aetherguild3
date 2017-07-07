from aiohttp import WSCloseCode
import logging

log = logging.getLogger(__name__)


async def init_sockets(app):
    app['sockets'] = set()
    log.info("Sockets: Socket set initialized")


async def close_sockets(app):
    # Copy the set and close by iterating that. This way we wont be removing from the set while iterating.
    for ws in set(app['sockets']):
        await ws.close(code=WSCloseCode.GOING_AWAY, message='Server shutdown')
    log.info("Sockets: Socket set closed")
