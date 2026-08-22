"""Compatibility helpers for generated features using SQLAlchemy directly.

The feature modules were generated against a few different database wrappers.
This module gives them one lazy, request-scoped interface without opening a
database connection while the application (or its tests) is importing.
"""

from flask import current_app, g
from sqlalchemy.orm import Session

from backend.core.db import get_engine


def _current_engine():
    """Use the app's configured engine, including its isolated test database."""
    return current_app.config.get("DATABASE_ENGINE") or get_engine()


class _Database:
    @property
    def session(self) -> Session:
        if "_database_session" not in g:
            g._database_session = Session(_current_engine())
        return g._database_session


db = _Database()


def get_db() -> Session:
    """Return the SQLAlchemy session for the current request."""
    return db.session


def get_db_connection():
    """Return a direct connection for features written against Core APIs."""
    return _current_engine().connect()


def close_request_database(_error=None) -> None:
    """Release any request-scoped ORM session."""
    session = g.pop("_database_session", None)
    if session is not None:
        session.close()
