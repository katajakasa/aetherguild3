
class Response(object):
    def __init__(self, protocol, stream):
        self._protocol = protocol
        self._stream = stream

    async def send_message(self, message):
        await self._protocol.send_message(self._stream, message)

    async def send_error(self, error_code, error_message, error_fields=None):
        await self._protocol.send_error(self._stream, error_code, error_message, error_fields)

    async def close(self):
        if self._protocol:
            await self._protocol.send_close(self._stream)
            self._protocol = None
