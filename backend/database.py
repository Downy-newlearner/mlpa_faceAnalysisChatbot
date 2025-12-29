"""
Database models and connection management using SQLAlchemy.
Implements storage for analysis results and chat logs.
"""

import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer, ForeignKey, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.pool import StaticPool

from .config import get_settings, DATABASE_PATH

# Create engine with SQLite optimizations
engine = create_engine(
    f"sqlite:///{DATABASE_PATH}",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False
)

# Enable WAL mode for better concurrency
with engine.connect() as conn:
    conn.execute(text("PRAGMA journal_mode=WAL"))
    conn.execute(text("PRAGMA synchronous=NORMAL"))
    conn.commit()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Analysis(Base):
    """Model for storing image analysis results."""
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_id = Column(String(36), unique=True, index=True, nullable=False)
    json_result = Column(Text, nullable=False)  # JSON string
    image_paths = Column(Text, nullable=True)   # JSON array of paths
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to chat logs
    chat_logs = relationship("ChatLog", back_populates="analysis", cascade="all, delete-orphan")
    
    @staticmethod
    def generate_id() -> str:
        """Generate a new unique analysis ID."""
        return str(uuid.uuid4())


class ChatLog(Base):
    """Model for storing chat history."""
    __tablename__ = "chat_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_id = Column(String(36), ForeignKey("analyses.analysis_id"), nullable=False, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to analysis
    analysis = relationship("Analysis", back_populates="chat_logs")


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully!")


if __name__ == "__main__":
    init_db()
