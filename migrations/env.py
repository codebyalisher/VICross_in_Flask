import logging  # This is the missing import
from logging.config import fileConfig
from alembic import context
from AdminDashboard import create_app
from AdminDashboard.database import db
from AdminDashboard.routes.models import User,OTP,TradeBooth  # Import the models here

config = context.config
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')

# Create the Flask app
app = create_app()

target_metadata = db.Model.metadata  # Ensure this is pointing to your app's metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = db.engine

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()