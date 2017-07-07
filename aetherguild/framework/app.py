import asyncio
import logging
from logging.config import dictConfig

from aiohttp import web
from dynaconf import settings

from aetherguild.framework.web.cache import init_cache, close_cache
from aetherguild.framework.web.database import init_db, close_db
from aetherguild.framework.web.listeners import websocket_listener
from aetherguild.framework.web.sockets import init_sockets, close_sockets
from aetherguild.framework.web.session import init_session_mgr, close_session_mgr

# Attempt to use uvloop if it is available
try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass

log = logging.getLogger(__name__)


def run_site(settings_file, ws_routes):
    settings.configure(settings_file)
    dictConfig(settings.LOGGING)

    # Get a reference to the main loop
    loop = asyncio.get_event_loop()

    # Set up the aiohttp application
    app = web.Application(loop=loop, debug=settings.DEBUG)
    app['ws_routes'] = ws_routes

    # Startup and shutdown callbacks
    for fn in [init_sockets, init_db, init_cache, init_session_mgr]:
        app.on_startup.append(fn)
    for fn in [close_sockets]:
        app.on_shutdown.append(fn)
    for fn in [close_cache, close_session_mgr, close_db]:
        app.on_cleanup.append(fn)

    # Routes
    app.router.add_get('/ws', websocket_listener)

    # Run application
    handler = app.make_handler()
    server = loop.create_server(
        protocol_factory=handler,
        host=settings.HOST,
        port=settings.PORT,
        backlog=settings.BACKLOG)
    loop.run_until_complete(app.startup())
    srv = loop.run_until_complete(server)

    log.info("Running server on %s:%d", settings.HOST, settings.PORT)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        log.info("Shutting down ...")
        srv.close()
        loop.run_until_complete(srv.wait_closed())
        loop.shutdown_asyncgens()
        loop.run_until_complete(app.shutdown())
        loop.run_until_complete(handler.shutdown(60.0))
        loop.run_until_complete(app.cleanup())
        loop.close()
