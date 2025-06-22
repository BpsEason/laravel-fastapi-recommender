import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from redis import Redis
from unittest.mock import MagicMock

from app.main import app
from app.models.db import Base
from app.models.user import User
from app.models.product import Product, Category
from app.models.order import OrderItem
from app.models.interaction import UserInteraction
from app.dependencies import get_db, get_redis_client

# --- Test Database Setup ---
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(name="session")
def session_fixture():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(name="client")
def client_fixture(session):
    def override_get_db():
        yield session
    
    mock_redis = MagicMock(spec=Redis)
    mock_redis.ping.return_value = True
    def override_get_redis_client():
        return mock_redis

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis_client] = override_get_redis_client
    
    yield TestClient(app)
    
    app.dependency_overrides = {}

@pytest.fixture
def populate_db(session):
    category1 = Category(name="Electronics")
    session.add(category1)
    session.commit()
    session.refresh(category1)

    user1 = User(name="Test User 1", email="test1@example.com", password="hashed_password")
    session.add(user1)
    session.commit()
    session.refresh(user1)

    product1 = Product(name="Laptop", description="Good laptop", price=1000.0, stock=10, category_id=category1.id)
    session.add(product1)
    session.commit()
    session.refresh(product1)

    session.add(OrderItem(user_id=user1.id, product_id=product1.id, quantity=1, price=product1.price))
    session.add(UserInteraction(user_id=user1.id, product_id=product1.id, interaction_type="view"))
    session.commit()
    
    return {
        "user1": user1, "product1": product1
    }

def test_get_recommendations_calculate_and_cache(client, populate_db):
    user1_id = populate_db["user1"].id
    mock_redis = app.dependency_overrides[get_redis_client]()
    mock_redis.get.return_value = None
    
    response = client.get(f"/api/v1/recommendations/{user1_id}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    mock_redis.setex.assert_called_once()

def test_health_check_success(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "connected", "redis": "connected"}
