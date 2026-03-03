from logging.config import fileConfig
from alembic import context

# Import only the database connection
from src.agentic_platform.core.db.postgres import write_postgres_db

# Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# No metadata since we're not using the ORM
target_metadata = None

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = "postgresql://offline"
    context.configure(
        url=url,
        target_metadata=None,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode using the existing connection."""
    # Use your existing connection for migrations
    with write_postgres_db.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=None,  # No ORM metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()