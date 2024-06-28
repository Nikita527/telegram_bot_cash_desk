from contextlib import asynccontextmanager

from models.data_base import SessionLocal


@asynccontextmanager
async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
