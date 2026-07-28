"""Database session management."""

from collections.abc import Generator

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.base import create_session

SessionLocal = create_session(settings.database_url)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that provides a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
