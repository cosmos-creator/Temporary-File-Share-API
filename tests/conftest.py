import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db import Base
from app.api.auth import get_db
from app.models.user import User

# in memory db
TEST_URL = "sqlite:///:memory:"

engine = create_engine(TEST_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(bind=engine)

@pytest.fixture()
def client():
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)

# get_db overriding function
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# swap dependencies
app.dependency_overrides[get_db] = override_get_db

