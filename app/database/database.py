"""
Database configuration and session management
Supports both SQLite and PostgreSQL
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import DATABASE_URL

# Create database engine
# SQLite: sqlite:///./bookings.db
# PostgreSQL: postgresql://user:password@localhost/dbname
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    echo=False  # Set to True for SQL query logging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


def get_db():
    """
    Dependency for getting database session
    
    Usage in FastAPI:
        def endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    # Import models so they are registered with Base
    from . import models
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print(f"✅ Database initialized: {DATABASE_URL}")
