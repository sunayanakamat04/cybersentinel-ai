"""Database session and connection management."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from cybersentinel.config import settings
from cybersentinel.database.models import Base

# Synchronous engine for fast local operations / SQLite / migrations
sync_engine = create_engine(
    settings.database_sync_url,
    echo=False,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_sync_url else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)


def init_db() -> None:
    """Creates database tables if they do not exist."""
    Base.metadata.create_all(bind=sync_engine)


def get_db():
    """Dependency generator for database sessions."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
