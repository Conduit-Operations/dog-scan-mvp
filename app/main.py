import os
import secrets
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from starlette.middleware.sessions import SessionMiddleware

from app.db import Dog, Owner, SessionLocal, create_tables, engine

templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

VET_PASSWORD = os.environ.get("VET_PASSWORD", "")
SESSION_SECRET = os.environ.get("SESSION_SECRET", "")


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

# A signed "is a vet" session cookie, valid for 8 hours. SESSION_SECRET signs it
# so it can't be forged; a missing secret falls back to a dev-only placeholder.
app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET or "dev-insecure-secret-set-SESSION_SECRET",
    max_age=8 * 60 * 60,
)


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


@app.get("/login", response_class=HTMLResponse)
def login_form(request: Request, token: str = ""):
    return templates.TemplateResponse(
        request=request, name="login.html", context={"token": token, "error": False}
    )


@app.post("/login")
def login_submit(request: Request, password: str = Form(""), token: str = Form("")):
    # The vet door's gate: compare against the shared password (constant-time).
    # On success, set the "is a vet" session and return to the dog's vet view.
    if VET_PASSWORD and secrets.compare_digest(
        password.encode("utf-8"), VET_PASSWORD.encode("utf-8")
    ):
        request.session["vet"] = True
        target = f"/d/{token}/vet" if token else "/"
        return RedirectResponse(target, status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"token": token, "error": True},
        status_code=401,
    )


@app.get("/d/{token}/vet", response_class=HTMLResponse)
def vet_view(request: Request, token: str):
    # The clinical view — the only place the medical record is read. Requires a
    # valid vet session; without one, send the visitor to log in first.
    if not request.session.get("vet"):
        return RedirectResponse(f"/login?token={token}", status_code=303)

    with SessionLocal() as session:
        dog = session.query(Dog).filter(Dog.token == token).first()
        if dog is None:
            data = None
        else:
            owner = session.query(Owner).filter(Owner.id == dog.owner_id).first()
            data = {
                "dog_name": dog.name,
                "breed": dog.breed,
                "microchip": dog.microchip,
                "owner_name": owner.name,
                "phone": owner.phone,
                "email": owner.email,
                "record": dog.record or {},
            }

    if data is None:
        return templates.TemplateResponse(
            request=request, name="not_found.html", status_code=404
        )
    return templates.TemplateResponse(request=request, name="vet.html", context=data)
