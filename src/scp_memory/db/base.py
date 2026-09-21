"""SQLAlchemy declarative base (ADR-004, SQLAlchemy 2.x)."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""
