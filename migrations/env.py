"""Alembic migration environment for the Rephina ERP.

The target metadata is the Flask-SQLAlchemy ``db.metadata``, populated by
importing the ``app.models`` package (which registers every model). The
database URL is taken from the ``DATABASE_URL`` environment variable
(``ALEMBIC_DATABASE_URL`` overrides it, handy for generating migrations
against a throwaway database).
"""
import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool
from dotenv import load_dotenv

# Make the project root importable so `config` and `app` resolve.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

# Import the SQLAlchemy handle and every model so the metadata is complete.
from config.database import db
import app.models  # noqa: F401  (side effect: registers all models on db.metadata)

config = context.config

# DATABASE_URL (or ALEMBIC_DATABASE_URL) wins over the alembic.ini placeholder.
db_url = os.getenv("ALEMBIC_DATABASE_URL") or os.getenv("DATABASE_URL")
if db_url:
    config.set_main_option("sqlalchemy.url", db_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = db.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
