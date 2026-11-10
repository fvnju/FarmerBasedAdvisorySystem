import sys
import os

# 🚨 Ensure 'app' package can be found
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path
import uvicorn
from alembic import command
from alembic.config import Config
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.engine import make_url

from app.audit import end_audit_context, register_audit_listeners, start_audit_context
from app.core.config import settings
from app.core.handlers import register_exception_handlers
from app.database import DATABASE_URL, SessionLocal
from app.route import api_router
from app.route.system import router as system_router
from app.service.system import SystemService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print(
    f"🔗 [DEBUG] Trying to connect to database: {make_url(DATABASE_URL).render_as_string(hide_password=True)}"
)  # Never write the password to the log


def run_migrations() -> None:
    project_root = Path(__file__).resolve().parent.parent
    alembic_ini_path = project_root / "alembic.ini"
    alembic_dir = project_root / "alembic"
    versions_dir = alembic_dir / "versions"

    print(f"🔍 [DEBUG] Looking for alembic.ini at: {alembic_ini_path}")

    if not alembic_ini_path.exists():
        raise FileNotFoundError(
            f"❌ [DEBUG] Alembic config not found at {alembic_ini_path}"
        )

    # 1. Ensure directories exist
    alembic_dir.mkdir(parents=True, exist_ok=True)
    versions_dir.mkdir(parents=True, exist_ok=True)

    # 2. Ensure script.py.mako exists
    mako_path = alembic_dir / "script.py.mako"
    if not mako_path.exists():
        print("📝 [DEBUG] Creating missing script.py.mako template...")
        mako_content = '''"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision: str = ${repr(up_revision)}
down_revision: Union[str, None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
'''
        mako_path.write_text(mako_content, encoding="utf-8")

    # 3. Ensure env.py exists
    env_path = alembic_dir / "env.py"
    if not env_path.exists():
        print("📝 [DEBUG] Creating missing env.py template...")
        env_content = """import sys
import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
load_dotenv()

from app.database import Base
import app.model

config = context.config
config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"})
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(config.get_section(config.config_ini_section, {}), prefix="sqlalchemy.", poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
"""
        env_path.write_text(env_content, encoding="utf-8")

    # 4. Configure Alembic with absolute path
    alembic_cfg = Config(str(alembic_ini_path))
    alembic_cfg.config_ini_section = "alembic"  # Force the section name
    alembic_cfg.set_main_option("script_location", str(alembic_dir))

    print(f"📂 [DEBUG] Checking for migrations in: {versions_dir}")

    if not any(versions_dir.iterdir()):
        print("📝 [DEBUG] No migrations found. Auto-generating initial migration...")
        command.revision(
            alembic_cfg, autogenerate=True, message="Initial auto-generated migration"
        )
        print("✅ [DEBUG] Migration file generated.")

    print("⚙️ [DEBUG] Applying database migrations...")
    command.upgrade(alembic_cfg, "head")
    print("✅ [DEBUG] Database migrations applied successfully.")


def ensure_rbac() -> bool:  # Make the roles if the database has none
    db = SessionLocal()
    try:
        return SystemService(db).ensure_rbac()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🌟 [DEBUG] FastAPI starting up...")
    try:
        await asyncio.to_thread(run_migrations)
    except Exception as e:
        print(f"❌ [DEBUG] Migration FAILED: {e}")
        raise
    if await asyncio.to_thread(ensure_rbac):
        print("🔐 [DEBUG] Roles and privileges created. Call POST /seed-data to create the first admin.")
    yield
    print("🛑 [DEBUG] FastAPI shutting down...")


app = FastAPI(lifespan=lifespan)
register_audit_listeners()  # Write an audit row for each insert, update and delete
register_exception_handlers(app)  # Convert domain errors to HTTP responses
app.include_router(system_router)  # Root, health check, and seed data
app.include_router(api_router)  # All resources under /api/v1


@app.middleware("http")
async def audit_context_middleware(request: Request, call_next):
    context, token = start_audit_context(
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    try:
        response = await call_next(request)
        response.headers["X-Request-ID"] = context.request_id  # Lets a user report the request
        return response
    finally:
        end_audit_context(token)


app.add_middleware(  # Added last, so it runs first and answers the browser preflight requests
    CORSMiddleware,
    allow_origins=settings.cors_origins,  # The React client. Set CORS_ORIGINS in .env for other addresses.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Authorization", "Content-Type"],
    expose_headers=["X-Request-ID"],
)


if __name__ == "__main__":
    print("🌐 [DEBUG] Starting Uvicorn server...")
    # Run from app folder or root, it doesn't matter now
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)
