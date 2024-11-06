import os
from logging.config import fileConfig

import dotenv
from sqlalchemy import engine_from_config
from sqlalchemy import pool, URL

from alembic import context

from dotenv import load_dotenv

from models.basemodel import BaseModel

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = BaseModel.metadata

# other values from the config, defined by the needs of .env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

dotenv.load_dotenv()

cmd_line_dbname = context.get_x_argument(
    as_dictionary=True).get('dbname')

dbname = cmd_line_dbname if cmd_line_dbname else os.environ.get('DB_DB_NAME')

connection_url = URL.create(
    drivername='+'.join(filter(None, (os.getenv("DB_DBMS_NAME"), os.getenv('DB_DRIVER')))),
    username=os.environ.get('DB_USERNAME'),
    password=os.environ.get('DB_USER_PASSWORD'),
    host=os.environ.get('DB_HOST'),
    port=int(os.environ.get('DB_PORT')),
    database=dbname,
)

config.set_main_option('sqlalchemy.url', connection_url.render_as_string(hide_password=False))


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
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
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
