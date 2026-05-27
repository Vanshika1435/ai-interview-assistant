from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.config import settings

# Engine = actual connection to PostgreSQL
engine = create_engine(settings.DATABASE_URL)

# SessionLocal = factory to create DB sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = parent class for all our models
Base = declarative_base()

# Dependency — FastAPI will call this to get a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()