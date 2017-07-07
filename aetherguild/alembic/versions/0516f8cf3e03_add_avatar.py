"""Add avatar

Revision ID: 0516f8cf3e03
Revises: 5ff4ae863817
Create Date: 2017-07-03 23:04:43.219790

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0516f8cf3e03'
down_revision = '5ff4ae863817'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('avatar', sa.Unicode(length=32), nullable=True))
    op.create_foreign_key(None, 'users', 'files', ['avatar'], ['key'])


def downgrade():
    op.drop_constraint(None, 'users', type_='foreignkey')
    op.drop_column('users', 'avatar')
