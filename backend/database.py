from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.config import settings

# Engine = actual connection to PostgreSQL
# pool_pre_ping recovers from dropped/stale connections (common with VPS + Render)
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=1800,
)

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