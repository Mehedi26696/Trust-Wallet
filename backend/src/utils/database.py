"""
Database configuration and session management for Supabase PostgreSQL.
"""

from sqlmodel import create_engine, Session, text
from typing import Generator
from ..config import settings

# Database configuration for Supabase PostgreSQL
DATABASE_URL = settings.DATABASE_URL
print("🐘 Using PostgreSQL database (Supabase)")

# PostgreSQL/Supabase engine configuration
engine = create_engine(
    DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True,
    pool_recycle=300,
)
print("✅ PostgreSQL engine created successfully")


def get_session() -> Generator[Session, None, None]:
    """
    Dependency to get database session.
    
    Yields:
        Session: Database session
    """
    with Session(engine) as session:
        yield session


def test_database_connection() -> bool:
    """Test if the database connection is working."""
    try:
        with Session(engine) as session:
            result = session.exec(text("SELECT 1")).first()
        print("✅ Database connection test successful")
        return result is not None
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        return False