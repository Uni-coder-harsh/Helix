from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from helix_platform.config import get_settings

# Retrieve application configurations
settings = get_settings()

# Create SQLAlchemy engine instance
# Normalize legacy 'postgres://' connection string format from providers like Neon DB
db_url = settings.DATABASE_URL
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

# If using SQLite, we require check_same_thread=False for FastAPI concurrency
connect_args = {"check_same_thread": False} if "sqlite" in db_url else {}

engine = create_engine(db_url, connect_args=connect_args)

# Create session maker instance
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base class for data models
Base = declarative_base()


def get_db() -> Generator[SessionLocal]:  # type: ignore[valid-type]
    """FastAPI dependency provider to yield a database session.

    Closes it after the request completes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
