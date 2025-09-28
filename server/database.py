import os
import time
from contextlib import contextmanager
from sqlalchemy import create_engine, Column, Integer, String, Text, MetaData, Table
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, Tuple
import pymysql

# Database configuration
DB_HOST = os.getenv("DB_HOST", "")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_NAME = os.getenv("DB_NAME", "feedback_db")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# Create database URL
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create SQLAlchemy engine with connection timeout settings
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_timeout=20,
    pool_size=5,
    max_overflow=10,
    connect_args={
        "connect_timeout": 10,
        "read_timeout": 10,
        "write_timeout": 10,
    },
    echo=False
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base
Base = declarative_base()

class Feedback(Base):
    """Feedback table model"""
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    intermediate_feedbacks = Column(Text, nullable=True)
    feedback = Column(Text, nullable=False)
    timestamp = Column(Integer, nullable=False)
    time_taken = Column(Integer, nullable=True)

def init_database():
    """Initialize the database and create the feedback table if it doesn't exist"""
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print(f"Database initialized successfully at {DB_HOST}")
        return True
    except SQLAlchemyError as e:
        print(f"Error initializing database: {e}")
        print("Please ensure:")
        print("1. MySQL server is running and accessible")
        print("2. Database credentials are correct (set via environment variables)")
        print("3. Database 'feedback_db' exists on the MySQL server")
        print("4. Network connectivity to the MySQL server is available")
        return False

@contextmanager
def get_db_connection():
    """Context manager for database sessions"""
    session = SessionLocal()
    try:
        yield session
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()

def add_entry(feedback_text: str, intermediate_feedbacks: str = None, time_taken: int = None) -> int:
    """Add a new entry to the database"""
    try:
        with get_db_connection() as session:
            feedback_entry = Feedback(
                feedback=feedback_text,
                intermediate_feedbacks=intermediate_feedbacks,
                timestamp=int(time.time()),
                time_taken=time_taken
            )
            session.add(feedback_entry)
            session.commit()
            session.refresh(feedback_entry)
            return feedback_entry.id
    except SQLAlchemyError as e:
        print(f"Error adding entry: {e}")
        raise

def get_most_recent_entry() -> Optional[Tuple[str, int, str, int]]:
    """Get the most recent feedback entry"""
    try:
        with get_db_connection() as session:
            feedback_entry = session.query(Feedback).order_by(
                Feedback.timestamp.desc()
            ).first()
            
            if feedback_entry is None:
                return None
            
            return (feedback_entry.feedback, feedback_entry.timestamp, feedback_entry.intermediate_feedbacks, feedback_entry.time_taken)
    except SQLAlchemyError as e:
        print(f"Error getting most recent entry: {e}")
        raise
