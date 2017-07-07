"""Initial tables

Revision ID: 5ff4ae863817
Revises: 
Create Date: 2017-07-03 22:57:59.607915

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '5ff4ae863817'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.Unicode(length=64), nullable=False),
        sa.Column('password', sa.String(length=256), nullable=False),
        sa.Column('email', sa.String(length=256), nullable=True),
        sa.Column('nickname', sa.Unicode(length=64), nullable=False),
        sa.Column('signature', sa.UnicodeText(), nullable=False),
        sa.Column('location', sa.Unicode(length=64), nullable=False),
        sa.Column('timezone', sa.Unicode(length=64), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_contact', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )
    op.create_table(
        'files',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('owner', sa.Integer(), nullable=True),
        sa.Column('key', sa.Unicode(length=32), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['owner'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key')
    )
    op.create_table(
        'forum_sections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.Unicode(length=128), nullable=False),
        sa.Column('sort_index', sa.Integer(), nullable=False),
        sa.Column('deleted', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_forum_sections_sort_index'), 'forum_sections', ['sort_index'], unique=False)
    op.create_table(
        'forum_boards',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('section', sa.Integer(), nullable=False),
        sa.Column('title', sa.Unicode(length=128), nullable=False),
        sa.Column('description', sa.UnicodeText(), nullable=False),
        sa.Column('sort_index', sa.Integer(), nullable=False),
        sa.Column('deleted', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['section'], ['forum_sections.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_forum_boards_sort_index'), 'forum_boards', ['sort_index'], unique=False)
    op.create_table(
        'forum_threads',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('board', sa.Integer(), nullable=False),
        sa.Column('user', sa.Integer(), nullable=False),
        sa.Column('title', sa.Unicode(length=128), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('views', sa.Integer(), nullable=False),
        sa.Column('sticky', sa.Boolean(), nullable=False),
        sa.Column('closed', sa.Boolean(), nullable=False),
        sa.Column('deleted', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['board'], ['forum_boards.id'], ),
        sa.ForeignKeyConstraint(['user'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_forum_threads_sort_index', 'forum_threads', ['sticky', 'updated_at', 'deleted'], unique=False)
    op.create_table(
        'forum_posts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('thread', sa.Integer(), nullable=False),
        sa.Column('user', sa.Integer(), nullable=False),
        sa.Column('message', sa.UnicodeText(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['thread'], ['forum_threads.id'], ),
        sa.ForeignKeyConstraint(['user'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_forum_posts_created_at'), 'forum_posts', ['created_at'], unique=False)
    op.create_index('ix_forum_posts_sort_index', 'forum_posts', ['created_at', 'deleted'], unique=False)
    op.create_table(
        'forum_last_reads',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('thread', sa.Integer(), nullable=False),
        sa.Column('user', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['thread'], ['forum_threads.id'], ),
        sa.ForeignKeyConstraint(['user'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_thread_user_constraint', 'forum_last_reads', ['thread', 'user'], unique=True)
    op.create_table(
        'forum_post_edits',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('post', sa.Integer(), nullable=False),
        sa.Column('user', sa.Integer(), nullable=False),
        sa.Column('message', sa.UnicodeText(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['post'], ['forum_posts.id'], ),
        sa.ForeignKeyConstraint(['user'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'news_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nickname', sa.Unicode(length=64), nullable=False),
        sa.Column('header', sa.Unicode(length=128), nullable=False),
        sa.Column('message', sa.UnicodeText(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'privileges',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.Unicode(length=32), nullable=False),
        sa.Column('description', sa.Unicode(length=64), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_table(
        'roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.Unicode(length=32), nullable=False),
        sa.Column('description', sa.Unicode(length=64), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_table(
        'role_privileges',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('privilege', sa.Integer(), nullable=False),
        sa.Column('role', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['privilege'], ['privileges.id'], ),
        sa.ForeignKeyConstraint(['role'], ['roles.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('privilege', 'role', name='uix_privilege_role_constraint')
    )
    op.create_table(
        'user_roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user', sa.Integer(), nullable=False),
        sa.Column('role', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['role'], ['roles.id'], ),
        sa.ForeignKeyConstraint(['user'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('user_roles')
    op.drop_table('role_privileges')
    op.drop_table('roles')
    op.drop_table('privileges')
    op.drop_table('news_items')
    op.drop_table('forum_post_edits')
    op.drop_index('ix_thread_user_constraint', table_name='forum_last_reads')
    op.drop_table('forum_last_reads')
    op.drop_index('ix_forum_posts_sort_index', table_name='forum_posts')
    op.drop_index(op.f('ix_forum_posts_created_at'), table_name='forum_posts')
    op.drop_table('forum_posts')
    op.drop_index('ix_forum_threads_sort_index', table_name='forum_threads')
    op.drop_table('forum_threads')
    op.drop_index(op.f('ix_forum_boards_sort_index'), table_name='forum_boards')
    op.drop_table('forum_boards')
    op.drop_index(op.f('ix_forum_sections_sort_index'), table_name='forum_sections')
    op.drop_table('forum_sections')
    op.drop_table('files')
    op.drop_table('users')
