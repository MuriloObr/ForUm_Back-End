from logging.config import fileConfig
from os import getenv

from sqlalchemy import engine_from_config, pool
from sqlalchemy import types as sqltypes

from alembic import context
from dotenv import load_dotenv

from src.db.models.user import User  # noqa: F401
from src.db.models.post import Post  # noqa: F401
from src.db.models.comment import Comment  # noqa: F401
from sqlmodel import SQLModel

load_dotenv()

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata

url = getenv("DATABASE_URL", default="sqlite://")

config.set_main_option("sqlalchemy.url", url)


def _compare_types(context_impl, insp_col, meta_col, insp_type, meta_type):
    if isinstance(insp_type, sqltypes.DateTime) and isinstance(meta_type, sqltypes.DateTime):
        return False
    return None


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
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
            compare_type=_compare_types,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
