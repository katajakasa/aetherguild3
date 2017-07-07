import logging

from aiohttp import WSMsgType, web

from aetherguild.framework.protocol.protocol import Protocol

log = logging.getLogger(__name__)


async def websocket_listener(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    request.app['sockets'].add(ws)

    protocol = Protocol(
        sessions=request.app['sessions'],
        db=request.app['db'],
        sockets=request.app['sockets'],
        socket=ws,
        routes=request.app['ws_routes']
    )

    # Listen to traffic as long as the socket is up
    async for msg in ws:
        log.info("Received: %s", msg.data)
        if msg.type == WSMsgType.TEXT:
            await protocol.handle_text(msg.data)
        elif msg.type == WSMsgType.BINARY:
            await protocol.handle_binary(msg.data)
        elif msg.type == WSMsgType.ERROR:
            log.info("Socket closed: %s", ws.exception())

    request.app['sockets'].remove(ws)
    return ws
