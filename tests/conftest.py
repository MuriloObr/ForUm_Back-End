import os

os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing"
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["DATABASE_URL"] = "sqlite://"

import pytest
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool

from src.db.models.user import User
from src.db.models.post import Post
from src.db.models.comment import Comment

import src.db.engine as _db_engine_mod
import utils.error_decorators as _err_mod
import src.user_actions as _user_mod


@pytest.fixture(name="test_engine")
def test_engine_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="db_session")
def db_session_fixture(test_engine):
    with Session(test_engine) as session:
        yield session


@pytest.fixture(autouse=True)
def _patch_engine(test_engine):
    _db_engine_mod.engine = test_engine
    _err_mod.engine = test_engine
    _user_mod.engine = test_engine
    yield
    _db_engine_mod.engine = test_engine
    _err_mod.engine = test_engine
    _user_mod.engine = test_engine


@pytest.fixture(name="client")
def client_fixture(test_engine):
    from fastapi.testclient import TestClient
    from src.main import app

    with TestClient(app) as c:
        yield c


@pytest.fixture
def registered_user(client):
    response = client.post("/api/register", json={
        "username": "testuser",
        "nickname": "Test User",
        "email": "test@example.com",
        "password": "securepass123",
    })
    assert response.status_code == 200
    return response.json()


@pytest.fixture
def logged_in_client(client, registered_user):
    response = client.post("/api/login", json={
        "user": "testuser",
        "password": "securepass123",
    })
    assert response.status_code == 200
    return client


@pytest.fixture
def sample_post(logged_in_client):
    response = logged_in_client.post("/api/posts/create", json={
        "title": "Test Post",
        "content": "Post content here",
    })
    assert response.status_code == 200
    return response.json()
