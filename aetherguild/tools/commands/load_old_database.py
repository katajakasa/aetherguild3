import binascii

import arrow
from aiomysql.sa import create_engine
from dynaconf import settings
from passlib.hash import aethery1, aethery2
from sqlalchemy import desc

from aetherguild.backend.database.tables import users, user_roles, roles, files, news_items, forum_boards, \
    forum_last_reads, \
    forum_post_edits, forum_posts, forum_sections, forum_threads, privileges, role_privileges
from aetherguild.deprecated.old_tables import old_users, really_old_users, old_forum_posts, old_news, \
    old_forum_sections, old_forum_boards, old_forum_threads, old_forum_edits, old_forum_reads
from . import BaseCommand


def make_utc(dt):
    return arrow.get(dt, 'Europe/Amsterdam').to('UTC').datetime


class LoadOldDatabase(BaseCommand):
    description = "Loads old database to new format"

    def __init__(self):
        super(LoadOldDatabase, self).__init__()
        self.level_to_role_map = {}
        self.user_mapping = {}
        self.section_mapping = {}
        self.board_mapping = {}
        self.thread_mapping = {}
        self.post_mapping = {}

    @staticmethod
    async def add_role(target, name, description):
        return await target.fetchrow(roles.insert().values(name=name, description=description))

    @staticmethod
    async def add_privilege(target, name, description, roles_list=None):
        dst = await target.fetchrow(privileges.insert().values(name=name, description=description))
        if roles_list:
            for role_id in roles_list:
                await target.fetchrow(role_privileges.insert().values(privilege=dst.id, role=role_id))

    async def _setup_base(self, target):
        admin = await self.add_role(target, "administrator", "All privileges, add for management rights")
        advanced = await self.add_role(target, "advanced", "Guild member, add for additional rights")
        basic = await self.add_role(target, "basic", "Basic forum read rights")

        self.level_to_role_map = {
            0: basic.id,  # guest to guest
            1: basic.id,  # newbie to guest
            2: advanced.id,  # user to user
            3: admin.id,  # admin to admin
            4: admin.id  # root to admin
        }

        await self.add_privilege(target, "manage_users", "Can manage users", roles_list=[admin.id])
        await self.add_privilege(target, "manage_forum", "Can manage forum", roles_list=[admin.id])
        await self.add_privilege(target, "manage_news", "Can manage news", roles_list=[admin.id])
        await self.add_privilege(target, "edit_forum_posts", "Can edit other peoples forum posts",
                                 roles_list=[admin.id])

    @staticmethod
    async def add_user_to_role(target, user, role):
        return await target.fetchrow(user_roles.insert().values(user=user, role=role))

    @staticmethod
    def log(name, text):
        print("[{0: <10}] {1}".format(name, text))

    async def _transfer_users(self, source, target):
        # Transfer users
        async for old_user in source.execute(old_users.select()):
            old_pw = binascii.hexlify(old_user.password)
            if old_pw == b'0000000000000000000000000000000000000000000000000000000000000000':
                old_pw = None

            # Format old password to new format
            if not old_pw:
                result = await source.execute(really_old_users.select().where(really_old_users.c.uid == old_user.id))
                row = await result.fetchone()
                new_password = aethery1.format_hash(_salt=row.salt.encode(), _checksum=row.password)
            else:
                new_password = aethery2.format_hash(_checksum=old_pw.decode())

            # Mark certain old accounts as deleted
            is_deleted = not bool(old_user.active) or bool(old_user.spambot)

            # Completely drop users who have no posts and still have old style password
            result = await source.execute(old_forum_posts.select().where(old_forum_posts.c.uid == old_user.id))
            row = await result.first()
            if not row:
                self.log("user", "Removing user {}".format(old_user.username))
                continue

            # Insert new user to the database. Note that some values go with defaults.
            result = await target.fetchrow(users.insert().values(
                username=old_user.username,
                password=new_password,
                nickname=old_user.alias,
                deleted=is_deleted,
                created_at=make_utc(old_user.registered),
                last_contact=make_utc(old_user.lastcontact),
            ))
            self.user_mapping[old_user.id] = result.id
            await self.add_user_to_role(target, result.id, self.level_to_role_map[old_user.level])

            self.log("user", "{} migrated".format(old_user.username))

    async def _transfer_news(self, source, target):
        async for old_item in source.execute(old_news.select()):
            await target.fetchrow(news_items.insert().values(
                nickname='Rinnagaros',
                header=old_item.header,
                message=old_item.message,
                created_at=make_utc(old_item.time)
            ))
            self.log("newsitem", "{} migrated".format(old_item.header))

    async def _transfer_forum(self, source, target):
        # Transfer sections
        async for old_section in source.execute(old_forum_sections.select()):
            result = await target.fetchrow(forum_sections.insert().values(
                title=old_section.title,
                sort_index=old_section.sort_index
            ))
            self.section_mapping[old_section.id] = result.id
            self.log("section", "{} migrated".format(old_section.title))

        # Transfer boards
        async for old_board in source.execute(old_forum_boards.select()):
            result = await target.fetchrow(forum_boards.insert().values(
                section=self.section_mapping[old_board.sid],
                title=old_board.title,
                description=old_board.description,
                sort_index=old_board.sort_index
            ))
            self.board_mapping[old_board.id] = result.id

            await self.add_privilege(target,
                                     "read_board_{}".format(result.id),
                                     "Can read board {}".format(old_board.title),
                                     roles_list=[self.level_to_role_map[old_board.min_read_level]])
            await self.add_privilege(target,
                                     "post_board_{}".format(result.id),
                                     "Can post to board {}".format(old_board.title),
                                     roles_list=[self.level_to_role_map[old_board.min_write_level]])
            await self.add_privilege(target,
                                     "manage_board_{}".format(result.id),
                                     "Can manage board {}".format(old_board.title),
                                     roles_list=[self.level_to_role_map[3]])

            self.log("board", "{} migrated".format(old_board.title))

        # Transfer threads
        async for old_thread in source.execute(old_forum_threads.select()):
            result = await source.execute(
                old_forum_posts.select()
                .where(old_forum_posts.c.tid == old_thread.id)
                .order_by(desc(old_forum_posts.c.id)))
            latest_thread_post = await result.first()

            result = await target.fetchrow(forum_threads.insert().values(
                board=self.board_mapping[old_thread.bid],
                user=self.user_mapping[old_thread.uid],
                title=old_thread.title,
                created_at=make_utc(old_thread.post_time),
                updated_at=make_utc(latest_thread_post.post_time),
                views=old_thread.views,
                sticky=bool(old_thread.sticky),
                closed=bool(old_thread.closed),
            ))
            self.thread_mapping[old_thread.id] = result.id
            self.log("thread", "{} migrated".format(old_thread.title))

        # Transfer posts
        async for old_post in source.execute(old_forum_posts.select()):
            result = await target.fetchrow(forum_posts.insert().values(
                user=self.user_mapping[old_post.uid],
                thread=self.thread_mapping[old_post.tid],
                created_at=make_utc(old_post.post_time),
                message=old_post.message
            ))
            self.post_mapping[old_post.id] = result.id
            self.log("post", "{} migrated".format(old_post.id))

        # Transfer edits
        async for old_edit in source.execute(old_forum_edits.select()):
            await target.fetchrow(forum_post_edits.insert().values(
                post=self.post_mapping[old_edit.pid],
                user=self.user_mapping[old_edit.uid],
                created_at=make_utc(old_edit.edit_time),
                message=old_edit.description
            ))
            self.log("post_edit", "{} migrated".format(old_edit.id))

        # Transfer forum reads
        async for old_read in source.execute(old_forum_reads.select()):
            if not old_read.uid in self.user_mapping:
                self.log("post_read", "{}/{} skipped due to deleted user".format(old_read.tid, old_read.uid))
            else:
                await target.fetchrow(forum_last_reads.insert().values(
                    thread=self.thread_mapping[old_read.tid],
                    user=self.user_mapping[old_read.uid],
                    created_at=make_utc(old_read.time),
                ))
                self.log("post_read", "{}/{} migrated".format(old_read.tid, old_read.uid))

    async def _load_source_to_target(self, source, target):
        await self._transfer_users(source, target)
        await self._transfer_news(source, target)
        await self._transfer_forum(source, target)

    @staticmethod
    async def _open_source_database():
        return await create_engine(
            db=settings.OLD_DATABASE['database'],
            user=settings.OLD_DATABASE['username'],
            password=settings.OLD_DATABASE['password'],
            host=settings.OLD_DATABASE['host'],
            port=settings.OLD_DATABASE['port'],
            minsize=1, maxsize=2)

    @staticmethod
    async def _clear_target_db(target):
        await target.fetchrow(news_items.delete())
        await target.fetchrow(forum_last_reads.delete())
        await target.fetchrow(forum_post_edits.delete())
        await target.fetchrow(forum_posts.delete())
        await target.fetchrow(forum_threads.delete())
        await target.fetchrow(forum_boards.delete())
        await target.fetchrow(forum_sections.delete())
        await target.fetchrow(role_privileges.delete())
        await target.fetchrow(user_roles.delete())
        await target.fetchrow(privileges.delete())
        await target.fetchrow(users.delete())
        await target.fetchrow(roles.delete())
        await target.fetchrow(files.delete())

    async def on_run(self, args, app):
        target_db = app['db']
        source_db = await self._open_source_database()
        async with target_db.transaction() as target_conn, source_db.acquire() as source_conn:
            await self._clear_target_db(target_conn)
            await self._setup_base(target_conn)
            await self._load_source_to_target(source_conn, target_conn)

        source_db.close()
        await source_db.wait_closed()
