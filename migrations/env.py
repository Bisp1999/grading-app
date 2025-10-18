import logging
from logging.config import fileConfig
from flask import current_app
from alembic import context
import os

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)




# Get database URL and metadata from current Flask app
try:
    # When running via flask db commands, current_app is available
    config.set_main_option('sqlalchemy.url', current_app.config['SQLALCHEMY_DATABASE_URI'])
    target_metadata = current_app.extensions['migrate'].db.metadata
    _app = None  # No need to create app
    _db = None  # Will use current_app's db
except RuntimeError:
    # Fallback for when running outside app context (e.g., alembic upgrade head)
    from app import create_app, db as _db
    _app = create_app(os.getenv('FLASK_ENV') or 'production')
    _app_context = _app.app_context()
    _app_context.push()
    config.set_main_option('sqlalchemy.url', _app.config['SQLALCHEMY_DATABASE_URI'])
    target_metadata = _db.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.




def run_migrations_offline():
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
        url=url, target_metadata=target_metadata, literal_binds=True
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    # Get the engine from the appropriate source
    try:
        connectable = current_app.extensions['migrate'].db.engine
    except (RuntimeError, KeyError):
        # Use the db we imported in the fallback
        if _db is not None:
            connectable = _db.engine
        else:
            # This shouldn't happen, but just in case
            from app import db
            connectable = db.engine

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
