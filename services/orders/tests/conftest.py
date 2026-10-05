import pytest
from fastapi.testclient import TestClient

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
