from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.db import create_tables, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create the three tables if the database is reachable. If it isn't, don't
    # crash the app — /health will simply report the database as unreachable.
    try:
        create_tables()
    except Exception:
        pass
    yield


app = FastAPI(title="Dog Tag MVP", lifespan=lifespan)


@app.get("/")
def root():
    return {"service": "Dog Tag MVP", "status": "running"}


@app.get("/health")
def health():
    database = "unreachable"
    if engine is not None:
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            database = "connected"
        except Exception:
            database = "unreachable"
    return {"status": "ok", "database": database}
