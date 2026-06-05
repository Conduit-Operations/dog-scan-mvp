import os

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    Text,
    create_engine,
)
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql import func

# Railway provides DATABASE_URL. SQLAlchemy expects the "postgresql://" scheme;
# Railway sometimes hands over the older "postgres://" alias, so normalise it.
DATABASE_URL = os.environ.get("DATABASE_URL", "")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# If DATABASE_URL is missing, the app still boots and /health reports the
# database as unreachable (rather than crashing). engine stays None in that case.
engine = create_engine(DATABASE_URL, pool_pre_ping=True) if DATABASE_URL else None
SessionLocal = sessionmaker(bind=engine, autoflush=False) if engine else None

Base = declarative_base()


class Owner(Base):
    __tablename__ = "owners"

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    phone = Column(Text, nullable=False)  # shown on the public page
    email = Column(Text)  # optional


class Dog(Base):
    __tablename__ = "dogs"

    id = Column(Integer, primary_key=True)  # internal only, never in a URL
    token = Column(Text, unique=True, nullable=False)  # the slug the URL is built from
    name = Column(Text, nullable=False)
    breed = Column(Text)
    microchip = Column(Text)  # stored, but never placed in a URL
    owner_id = Column(Integer, ForeignKey("owners.id"), nullable=False)
    record = Column(JSON)  # clinical data; shape stays JSON until it's known
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    dog_id = Column(Integer, ForeignKey("dogs.id"), nullable=False)
    type = Column(Text, nullable=False)  # "open" or "edit"
    field = Column(Text)  # which field changed (null for "open")
    old_value = Column(Text)  # null for "open"
    new_value = Column(Text)  # null for "open"
    actor = Column(Text)  # "vet" or "public"
    created_at = Column(DateTime(timezone=True), server_default=func.now())


def create_tables() -> None:
    """Create the three tables if they don't already exist. Safe to call on every boot."""
    if engine is None:
        return
    Base.metadata.create_all(engine)
