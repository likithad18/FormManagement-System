from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from alembic import context
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from database import Base, DATABASE_URL
from models import Submission

config = context.config
fileConfig(config.config_file_name)
target_metadata = Base.metadata

def run_migrations_offline():
    url = DATABASE_URL
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"}
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    from sqlalchemy.ext.asyncio import create_async_engine
    connectable = create_async_engine(DATABASE_URL, poolclass=pool.NullPool)
    async def run_migrations():
        async with connectable.connect() as connection:
            def do_run_migrations(connection):
                context.configure(connection=connection, target_metadata=target_metadata)
                context.run_migrations()
            await connection.run_sync(do_run_migrations)
    import asyncio
    asyncio.run(run_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online() 