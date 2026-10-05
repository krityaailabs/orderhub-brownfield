from contextlib import contextmanager

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event

from orderhub import seed
from orderhub.api import create_app
from orderhub.config import Settings


@pytest.fixture
def app(tmp_path):
    settings = Settings(database_url="sqlite://", currency="USD", billing_handoff_dir=str(tmp_path))
    application = create_app(settings)
    with application.state.session_factory() as session:
        seed.load(session)
    return application


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def session(app):
    with app.state.session_factory() as s:
        yield s


@pytest.fixture
def count_queries(app):
    """Count the SQL statements a block of code sends to the database.

        with count_queries() as statements:
            client.get("/orders")
        assert len(statements) <= 4, statements
    """
    engine = app.state.session_factory.kw["bind"]

    @contextmanager
    def counting():
        statements: list[str] = []

        def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            statements.append(statement)

        event.listen(engine, "before_cursor_execute", before_cursor_execute)
        try:
            yield statements
        finally:
            event.remove(engine, "before_cursor_execute", before_cursor_execute)

    return counting
