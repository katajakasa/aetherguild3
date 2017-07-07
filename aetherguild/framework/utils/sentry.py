from raven.handlers.logging import SentryHandler
from raven_aiohttp import AioHttpTransport
from raven import Client


class AsyncSentryHandler(SentryHandler):
    def __init__(self, *args, **kwargs):
        kwargs['client'] = Client(transport=AioHttpTransport)
        super(AsyncSentryHandler, self).__init__(*args, **kwargs)
