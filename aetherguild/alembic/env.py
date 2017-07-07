from __future__ import with_statement

import sys
from logging.config import fileConfig

from alembic import context
from dynaconf import settings
from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine.url import URL

sys.path.append('.')

from aetherguild.backend.database import tables

settings.configure("aetherguild.settings")

config = context.config
fileConfig(config.config_file_name)
target_metadata = tables.metadata

db_url = URL(
    drivername='postgresql+psycopg2',
    username=settings.DATABASE['username'],
    password=settings.DATABASE['password'],
    host=settings.DATABASE['host'],
    port=settings.DATABASE['port'],
    database=settings.DATABASE['database'],
)
config.set_main_option('sqlalchemy.url', str(db_url))


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            compare_type=True,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
