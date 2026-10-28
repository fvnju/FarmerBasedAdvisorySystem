import sys  # Import sys to modify the Python path
import os  # Import os to interact with the operating system
from dotenv import load_dotenv  # Import load_dotenv to read the .env file
from logging.config import fileConfig  # Import to read logging configuration
from sqlalchemy import engine_from_config, pool  # Import SQLAlchemy engine tools
from alembic import context  # Import Alembic context

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
load_dotenv()  # Load environment variables

from app.database import Base  # Import the Base class from our app
import app.model  # Import all models so Alembic detects them (see app/model/__init__.py)

config = context.config  # Get the current Alembic configuration

# 🚨 FIX: Escape % signs to prevent ConfigParser interpolation errors
db_url = os.getenv("DATABASE_URL")
if db_url:
    db_url = db_url.replace("%", "%%")
    config.set_main_option("sqlalchemy.url", db_url)

if config.config_file_name is not None:  # Check if config file exists
    fileConfig(config.config_file_name)  # Setup logging

target_metadata = Base.metadata  # Tell Alembic to compare the DB against our models


def run_migrations_offline() -> None:  # Function for offline migrations
    url = config.get_main_option("sqlalchemy.url")  # Get DB URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )  # Configure context
    with context.begin_transaction():  # Start transaction
        context.run_migrations()  # Run migrations


def run_migrations_online() -> None:  # Function for online migrations
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )  # Create engine
    with connectable.connect() as connection:  # Connect to DB
        context.configure(
            connection=connection, target_metadata=target_metadata
        )  # Configure context
        with context.begin_transaction():  # Start transaction
            context.run_migrations()  # Run migrations


if context.is_offline_mode():  # Check if running offline
    run_migrations_offline()  # Run offline
else:  # Otherwise
    run_migrations_online()  # Run online
