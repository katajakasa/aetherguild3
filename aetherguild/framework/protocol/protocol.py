import asyncio
import logging
import ujson

from aiohttp import WSCloseCode
from cerberus import Validator

from aetherguild.framework.protocol.request import Request
from aetherguild.framework.protocol.response import Response
from aetherguild.framework.protocol.schemas import base_request

log = logging.getLogger(__name__)


class Protocol(object):
    MAX_STREAMS = 8

    TYPE_MESSAGE = 'message'
    TYPE_ERROR = 'error'
    TYPE_BROADCAST = 'broadcast'
    TYPE_OPEN = 'open'
    TYPE_CLOSE = 'close'

    def __init__(self, socket, sockets, sessions, db, routes):
        self.socket = socket
        self.sockets = sockets
        self.routes = routes
        self.db = db
        self.sessions = sessions
        self.generators = {}

    async def broadcast(self, route, message, avoid_self=True):
        # TODO: Change to match protocol
        msg = self._form_message(message, self.TYPE_BROADCAST, route=route)

        futures = []
        for sock in self.sockets:
            if avoid_self and self.socket == sock:
                continue
            futures.append(sock.send_str(msg))
        await asyncio.wait(futures)

    async def send_message(self, stream, message):
        raw_message = self._form_message(message, self.TYPE_MESSAGE, stream=stream)
        await self.socket.send_str(raw_message)

    async def send_close(self, stream):
        raw_message = self._form_message({}, self.TYPE_CLOSE, stream=stream)
        await self.socket.send_str(raw_message)

    async def send_error(self, stream, error_code, error_message, error_fields=None):
        if not error_fields:
            error_fields = []

        content = {
            'field_errors': [{'field': e[0], 'message': e[1]} for e in error_fields],
            'code': error_code,
            'errors': [error_message],
        }

        raw_message = self._form_message(
            message=content,
            message_type=self.TYPE_ERROR,
            stream=stream)

        await self.socket.send_str(raw_message)

    @staticmethod
    def _form_message(message, message_type, route=None, stream=None):
        raw_message = {
            'message': message,
            'type': message_type,
        }
        if route:
            raw_message['route'] = route
        if stream:
            raw_message['stream'] = stream
        return ujson.dumps(raw_message, ensure_ascii=False)

    async def _handle_open_stream(self, message):
        log.info("Handling %s", message)
        route = message['route']
        data = message['message']
        stream = message['stream']
        session_key = message.get('session')
        log.info("Opening stream %s", stream)

        # Make sure requested route exists
        if route not in self.routes:
            await self.send_error(stream, 404, 'Route not found')
            return

        # Make sure user doesn't have too many streams open
        if len(self.generators) >= self.MAX_STREAMS:
            await self.send_error(stream, 400, 'Too many open streams')
            return

        # Check message schema
        if self.routes[route].schema:
            validator = Validator(schema=self.routes[route].schema)
            if not validator.validate({"message": data}):
                log.error("Invalid message received: %s", validator.errors, extra={'body': message})
                await self.send_error(stream, 400, "Bad request", error_fields=validator.errors)
                return

        # Get a DB connection and a new session.
        async with self.db.acquire() as db_connection, self.sessions.acquire(session_key) as session:
            req = Request(
                db=db_connection,
                session=session,
                message=data,
                stream=stream,
                route=route)

            response = Response(
                protocol=self,
                stream=stream)

            try:
                fn = self.routes[route].handler
                async with db_connection.transaction():
                    await fn(req, response)
                    await response.close()
            except Exception as e:
                log.exception("Handler failed: %s", str(e), extra={'body': message})
                await self.send_error(stream, 500, 'Internal server error')

    async def handle_text(self, raw_message):
        # Decode the message. If decoding fails, close connection with appropriate message.
        try:
            message = ujson.loads(raw_message)
        except ValueError as e:
            log.exception("Unable to decode message: %s", str(e), extra={'body': raw_message})
            await self.close(WSCloseCode.INVALID_TEXT, 'Bad request: JSON could not be decoded')
            return

        # Validate the message. If validation fails, close the connection with appropriate message.
        validator = Validator(schema=base_request)
        if not validator.validate(message):
            log.error("Invalid message received: %s", validator.errors, extra={'body': message})
            await self.close(WSCloseCode.PROTOCOL_ERROR,
                             'Bad request: Message validation failed: {}'.format(validator.errors))
            return

        # Check message type and handle as required. If invalid type, reply with error/404.
        message_type = message['type']
        stream = message['stream']
        if message_type == self.TYPE_OPEN:
            if stream in self.generators:
                await self.send_error(stream, 400, "Stream key is already in use")
                return

            # Add the generator future to a dict so that we can easily reach and cancel it if necessary
            self.generators[stream] = asyncio.ensure_future(self._handle_open_stream(message))
            await self.generators[stream]
            del self.generators[stream]
        elif message_type == self.TYPE_CLOSE:
            if stream not in self.generators:
                return

            # Simply cancel the stream. Await in
            log.info("Closing stream %s", stream)
            await self.generators[stream].cancel()
        else:
            self.send_error(message['stream'], 404, "Invalid message type {}".format(message_type))

    async def handle_binary(self, raw_message):
        pass

    async def close(self, code, message):
        """
        Closes the websocket.

        Args:
            code: Websocket connection closing code
            message: Websocket connection closing message
        """
        for k, v in self.generators.items():
            await v.cancel()
        self.generators = {}
        await self.socket.close(code=code, message=message)
