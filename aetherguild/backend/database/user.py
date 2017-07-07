import logging
from .tables import users, user_roles

log = logging.getLogger(__name__)


class UserException(Exception):
    pass


class User(object):
    def __init__(self, db, data, roles):
        self.db = db
        self.data = data
        self.roles = roles or []

    @staticmethod
    async def get_by_username(db_session, username):
        data = {}
        return User(db_session, data, None)

    @staticmethod
    async def create(session, username, password, email, nickname, roles=None):
        data = dict(
            username=username,
            password=password,
            email=email,
            nickname=nickname
        )
        result = await session.fetchrow(users.insert().values(**data))
        data['id'] = result.id
        user = User(session, data, None)
        for role in roles:
            user.add_role(role)
        return user

    async def save(self):
        pass

    async def _get_role_id_by_name(self, role_name):
        return 0

    async def has_role(self, role_name):
        return role_name in self.roles

    async def add_role(self, role_name):
        role_id = await self._get_role_id_by_name(role_name)
        await self.db.fetchrow(user_roles.insert().values(user=self.data['id'], role=role_id))
        self.roles.append(role_name)

    async def remove_role(self, role_name):
        role_id = await self._get_role_id_by_name(role_name)
        # delete here
        self.roles.remove(role_name)
