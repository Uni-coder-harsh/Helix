from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from helix_platform.config import get_settings

# Retrieve application configurations
settings = get_settings()

# Create SQLAlchemy engine instance
# If using SQLite, we require check_same_thread=False for FastAPI concurrency
connect_args = {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)

# Create session maker instance
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base class for data models
Base = declarative_base()


def get_db() -> Generator[SessionLocal, None, None]:  # type: ignore[valid-type]
    """FastAPI dependency provider to yield a database session and close it after request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
