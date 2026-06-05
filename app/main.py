from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import text

from app.db import Dog, Owner, SessionLocal, create_tables, engine

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
    # Resolve the scanned code to one dog and show the two-door fork (vet / not-a-vet).
    # An unknown code shows a friendly "we don't recognise this tag" page, never an error.
    with SessionLocal() as session:
        dog = session.query(Dog).filter(Dog.token == token).first()
        name = dog.name if dog else None

    if name is None:
        return templates.TemplateResponse(
            request=request, name="not_found.html", status_code=404
        )
    return templates.TemplateResponse(
        request=request, name="landing.html", context={"dog_name": name, "token": token}
    )


@app.get("/d/{token}/public", response_class=HTMLResponse)
def public(request: Request, token: str):
    # The public door: owner contact only. This path never reads the dog's
    # medical record — medical data has no route to a non-vet.
    with SessionLocal() as session:
        dog = session.query(Dog).filter(Dog.token == token).first()
        if dog is None:
            contact = None
        else:
            owner = session.query(Owner).filter(Owner.id == dog.owner_id).first()
            contact = {
                "dog_name": dog.name,
                "owner_name": owner.name,
                "phone": owner.phone,
                "email": owner.email,
            }

    if contact is None:
        return templates.TemplateResponse(
            request=request, name="not_found.html", status_code=404
        )
    return templates.TemplateResponse(request=request, name="public.html", context=contact)
