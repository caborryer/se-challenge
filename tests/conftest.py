import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models.user import User

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user_data():
    return {
        "username": "john_doe",
        "email": "john.doe@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "role": "user",
        "active": True
    }


@pytest.fixture
def sample_user_data_2():
    return {
        "username": "jane_smith",
        "email": "jane.smith@example.com",
        "first_name": "Jane",
        "last_name": "Smith",
        "role": "admin",
        "active": True
    }


@pytest.fixture
def created_user(client, sample_user_data):
    response = client.post("/api/v1/users/", json=sample_user_data)
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def multiple_users(client, sample_user_data, sample_user_data_2):
    users = []
    
    response1 = client.post("/api/v1/users/", json=sample_user_data)
    assert response1.status_code == 201
    users.append(response1.json())
    
    response2 = client.post("/api/v1/users/", json=sample_user_data_2)
    assert response2.status_code == 201
    users.append(response2.json())
    
    return users

