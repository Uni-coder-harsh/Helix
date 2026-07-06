import os
import sys
from collections.abc import Generator
from pathlib import Path

# Add backend directory to sys.path so tests can find platform and services modules
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Ensure test environment is configured before any import loads configuration
os.environ["HELIX_ENV"] = "test"
os.environ["DATABASE_URL"] = "sqlite:///test.db"

import pytest
from fastapi.testclient import TestClient

from helix_platform.persistence import Base, engine
from services.main import app


@pytest.fixture(scope="session", autouse=True)
def setup_db() -> Generator[None, None, None]:
    """Sets up test SQLite database before session and tears it down after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    # Remove test database file
    db_file = Path("test.db")
    if db_file.exists():
        db_file.unlink()


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Generates a FastAPI TestClient."""
    with TestClient(app) as test_client:
        yield test_client
