# -*- coding: utf-8 -*-

import arrow
from sqlalchemy import MetaData, Table, Column, Integer, ForeignKey, DateTime, UnicodeText, Boolean, UniqueConstraint,\
    Index, Unicode, String


def utc_now():
    return arrow.utcnow().datetime


metadata = MetaData()


users = Table(
    'users',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('username', Unicode(64), unique=True, nullable=False),
    Column('password', String(256), nullable=False),
    Column('email', String(256), nullable=True, unique=True),
    Column('nickname', Unicode(64), nullable=False),
    Column('avatar', ForeignKey('files.key'), default=None, nullable=True),
    Column('signature', UnicodeText, nullable=False, default=''),
    Column('location', Unicode(64), nullable=False, default=''),
    Column('timezone', Unicode(64), nullable=False, default='Europe/Amsterdam'),
    Column('created_at', DateTime(timezone=True), default=utc_now, nullable=False),
    Column('last_contact', DateTime(timezone=True), default=utc_now, nullable=False),
    Column('deleted', Boolean, default=False, nullable=False),
)

user_roles = Table(
    'user_roles',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('user', ForeignKey('users.id'), nullable=False),
    Column('role', ForeignKey('roles.id'), nullable=False),
)

roles = Table(
    'roles',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('name', Unicode(32), unique=True, nullable=False),
    Column('description', Unicode(64), nullable=False, default=''),
)

role_privileges = Table(
    'role_privileges',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('privilege', ForeignKey('privileges.id'), nullable=False),
    Column('role', ForeignKey('roles.id'), nullable=False),
    UniqueConstraint('privilege', 'role', name='uix_privilege_role_constraint')
)

privileges = Table(
    'privileges',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('name', Unicode(32), unique=True, nullable=False),
    Column('description', Unicode(64), nullable=False, default=''),
)

files = Table(
    'files',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('owner', ForeignKey('users.id'), nullable=True, default=None),
    Column('key', Unicode(32), unique=True, nullable=False),
    Column('created_at', DateTime(timezone=True), default=utc_now, nullable=False)
)

news_items = Table(
    'news_items',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('nickname', Unicode(64), nullable=False),
    Column('header', Unicode(128), nullable=False),
    Column('message', UnicodeText, nullable=False),
    Column('created_at', DateTime(timezone=True), default=utc_now, nullable=False),
    Column('deleted', Boolean, default=False, nullable=False)
)

forum_sections = Table(
    'forum_sections',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('title', Unicode(128), nullable=False),
    Column('sort_index', Integer, default=0, nullable=False, index=True),
    Column('deleted', Boolean, default=False, nullable=False)
)

forum_boards = Table(
    'forum_boards',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('section', ForeignKey('forum_sections.id'), nullable=False),
    Column('title', Unicode(128), nullable=False),
    Column('description', UnicodeText, nullable=False),
    Column('sort_index', Integer, default=0, nullable=False, index=True),
    Column('deleted', Boolean, default=False, nullable=False)
)

forum_threads = Table(
    'forum_threads',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('board', ForeignKey('forum_boards.id'), nullable=False),
    Column('user', ForeignKey('users.id'), nullable=False),
    Column('title', Unicode(128), nullable=False),
    Column('created_at', DateTime(timezone=True), default=utc_now, nullable=False),
    Column('updated_at', DateTime(timezone=True), default=utc_now, nullable=False),
    Column('views', Integer, default=0, nullable=False),
    Column('sticky', Boolean, default=False, nullable=False),
    Column('closed', Boolean, default=False, nullable=False),
    Column('deleted', Boolean, default=False, nullable=False),
    Index('ix_forum_threads_sort_index', 'sticky', 'updated_at', 'deleted')
)

forum_posts = Table(
    'forum_posts',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('thread', ForeignKey('forum_threads.id'), nullable=False),
    Column('user', ForeignKey('users.id'), nullable=False),
    Column('message', UnicodeText, nullable=False),
    Column('created_at', DateTime(timezone=True), default=utc_now, nullable=False, index=True),
    Column('deleted', Boolean, default=False, nullable=False),
    Index('ix_forum_posts_sort_index', 'created_at', 'deleted')
)

forum_post_edits = Table(
    'forum_post_edits',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('post', ForeignKey('forum_posts.id'), nullable=False),
    Column('user', ForeignKey('users.id'), nullable=False),
    Column('message', UnicodeText, nullable=True),
    Column('created_at', DateTime(timezone=True), default=utc_now, nullable=False)
)

forum_last_reads = Table(
    'forum_last_reads',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('thread', ForeignKey('forum_threads.id'), nullable=False),
    Column('user', ForeignKey('users.id'), nullable=False),
    Column('created_at', DateTime(timezone=True), default=utc_now, nullable=False),
    Index('ix_thread_user_constraint', 'thread', 'user', unique=True)
)
