# -*- coding: utf-8 -*-

from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text, Boolean, Binary, Table, MetaData,\
    PrimaryKeyConstraint


metadata = MetaData()


old_users = Table(
    "users",
    metadata,
    Column('id', Integer, primary_key=True),
    Column('username', String(32)),
    Column('password', Binary(32)),
    Column('alias', String(32)),
    Column('level', Integer),
    Column('active', Integer),
    Column('registered', DateTime),
    Column('lastcontact', DateTime),
    Column('lastlogoffpoint', DateTime),
    Column('spambot', Boolean)
)


really_old_users = Table(
    "old_users",
    metadata,
    Column('uid', Integer, primary_key=True),
    Column('password', String(40)),
    Column('salt', String(12)),
)


old_forum_sections = Table(
    "forum_sections",
    metadata,
    Column('id', Integer, primary_key=True),
    Column('title', String(64)),
    Column('sort_index', Integer),
)


old_forum_boards = Table(
    "forum_boards",
    metadata,
    Column('id', Integer, primary_key=True),
    Column('sid', ForeignKey('forum_sections.id')),
    Column('title', String(64)),
    Column('description', String(256)),
    Column('min_read_level', Integer),
    Column('min_write_level', Integer),
    Column('sort_index', Integer)
)


old_forum_threads = Table(
    "forum_threads",
    metadata,
    Column('id', Integer, primary_key=True),
    Column('bid', ForeignKey('forum_boards.id')),
    Column('uid', ForeignKey('user.id')),
    Column('title', String(64)),
    Column('post_time', DateTime),
    Column('views', Integer),
    Column('sticky', Boolean),
    Column('closed', Boolean)
)


old_forum_posts = Table(
    "forum_posts",
    metadata,
    Column('id', Integer, primary_key=True),
    Column('tid', ForeignKey('forum_threads.id')),
    Column('uid', ForeignKey('user.id')),
    Column('message', Text),
    Column('post_time', DateTime),
    Column('ip', String(15))
)


old_forum_edits = Table(
    "forum_post_edits",
    metadata,
    Column('id', Integer, primary_key=True),
    Column('pid', ForeignKey('forum_posts.id')),
    Column('uid', ForeignKey('user.id')),
    Column('edit_time', DateTime),
    Column('description', String(256)),
)


old_forum_reads = Table(
    "forum_last_reads",
    metadata,
    Column('tid', ForeignKey('forum_threads.id')),
    Column('uid', ForeignKey('user.id')),
    Column('time', DateTime),
    PrimaryKeyConstraint('tid', 'uid')
)


old_news = Table(
    "news",
    metadata,
    Column('id', Integer, primary_key=True),
    Column('header', String(64)),
    Column('message', Text),
    Column('time', DateTime)
)
