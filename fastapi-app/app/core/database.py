from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    pass


def _build_db_url() -> str:
    # Map Laravel-style DB_* env vars into a SQLAlchemy URL
    driver = settings.DB_CONNECTION
    
    if driver == "sqlite":
        return f"sqlite:///./{settings.DB_DATABASE}"
        
    user = settings.DB_USERNAME
    password = settings.DB_PASSWORD
    host = settings.DB_HOST
    port = settings.DB_PORT
    db = settings.DB_DATABASE

    return f"{driver}://{user}:{password}@{host}:{port}/{db}"


# Create engine with sqlite-specific configuration if needed
engine_args = {"pool_pre_ping": True}
if settings.DB_CONNECTION == "sqlite":
    engine_args["connect_args"] = {"check_same_thread": False}

engine = create_engine(_build_db_url(), **engine_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



