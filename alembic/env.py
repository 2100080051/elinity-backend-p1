import sys
import os
from logging.config import fileConfig
from alembic import context
from utils.settings import DATABASE_URL
from database.session import Base
from sqlalchemy import engine_from_config, pool
# Import models so Alembic's autogenerate can detect new tables
try:
    import models.conversation
    import models.evaluation
    import models.game_session
    import models.blogs
    import models.chat
    import models.journal
    import models.user
    import models.notifications
    import models.question_card
    import models.platform
except Exception as e:
    print(f"Metadata import warning: {e}")
    pass

# Add path to app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

config = context.config
fileConfig(config.config_file_name)

config.set_main_option('sqlalchemy.url', DATABASE_URL)

target_metadata = Base.metadata

# Helpful commands:
# 1) Inspect current DB revision:
#    alembic current
# 2) If your DB already has the expected schema (avoid running destructive older migrations):
#    alembic stamp head
# 3) Generate a migration for newly added models only:
#    alembic revision --autogenerate -m "add conversation memory tables"
# 4) Inspect the generated file under alembic/versions/ and remove any DROP/ALTER you don't want.
# 5) Apply the migration:
#    alembic upgrade head


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
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