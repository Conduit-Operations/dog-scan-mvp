from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import text

from app.db import Dog, SessionLocal, create_tables, engine

templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


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


@app.get("/d/{token}", response_class=HTMLResponse)
def scan(request: Request, token: str):
    # Resolve the scanned code to one dog and show its name. An unknown code
    # shows a friendly "we don't recognise this tag" page, never an error.
    with SessionLocal() as session:
        dog = session.query(Dog).filter(Dog.token == token).first()
        name = dog.name if dog else None

    if name is None:
        return templates.TemplateResponse(
            request=request, name="not_found.html", status_code=404
        )
    return templates.TemplateResponse(
        request=request, name="landing.html", context={"dog_name": name}
    )
