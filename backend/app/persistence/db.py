import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.persistence.base import Base
from app.persistence import tables 

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://video2story_user:video2story@localhost:5432/video2story",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()