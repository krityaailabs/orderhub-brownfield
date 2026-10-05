"""Database engine and session factory."""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    pass


def make_engine(url: str):
    if url == "sqlite://":
        # In-memory database shared across connections (used by the tests).
        return create_engine(url, connect_args={"check_same_thread": False}, poolclass=StaticPool)
    if url.startswith("sqlite"):
        return create_engine(url, connect_args={"check_same_thread": False})
    return create_engine(url)


def make_session_factory(engine):
    return sessionmaker(bind=engine, expire_on_commit=False)
