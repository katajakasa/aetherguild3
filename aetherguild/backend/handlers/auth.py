import logging
from passlib.context import CryptContext
from dynaconf import settings

from aetherguild.backend.database.user import get_user_by_name

log = logging.getLogger(__name__)


async def login_handler(request, response):
    pwd_context = CryptContext(schemes=settings.PASSWORD_HASH_PREF, deprecated="auto")
    username = request.message['username']
    password = request.message['password']

    user = await get_user_by_name(request.db, username)
    if not user:
        await response.send_error(400, "Invalid username or password")
        return

    if not pwd_context.verify(password, user['password']):
        await response.send_error(400, "Invalid username or password")
        return

    response.send_message({})


async def register_handler(request, response):
    pass


async def logout_handler(request, response):
    pass

