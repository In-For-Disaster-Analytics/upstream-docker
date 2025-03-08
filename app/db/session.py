from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Create database engine
engine = create_engine(settings.db_url)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency for getting DB sessions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
