import ujson
import logging

log = logging.getLogger(__name__)


class Session(object):
    def __init__(self, cache, key):
        self.data = {}
        self.key = key
        self.cache = cache
        self.changed = False

    def __contains__(self, item):
        return item in self.data

    def __iter__(self):
        return iter(self.data)

    def __getitem__(self, key):
        return self.data[key]

    def __len__(self):
        return len(self.data)

    def __setitem__(self, key, item):
        self.data[key] = item

    def __delitem__(self, key):
        del self.data[key]

    async def flush(self):
        if self.data and self.key:
            await self._save()

    async def __aenter__(self):
        if self.key:
            await self._load()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def _save(self):
        raw_data = ujson.dumps(self.data, ensure_ascii=False)
        await self.cache.set(self.key, raw_data)

    async def _load(self):
        raw_data = await self.cache.get(self.key)
        self.data = ujson.loads(raw_data.decode())


class SessionManager(object):
    def __init__(self, cache):
        self.cache = cache

    def acquire(self, key):
        return Session(self.cache, key)


async def init_session_mgr(app):
    app['sessions'] = SessionManager(app['cache'])
    log.info("SessionMgr: Session manager initialized")


async def close_session_mgr(app):
    app['sessions'] = None
    log.info("SessionMgr: Session manager closed")
