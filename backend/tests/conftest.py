import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
import sys

# Set testing environment
os.environ["TESTING"] = "true"
os.environ["JWT_SECRET"] = "test_secret_key_for_testing_only_change_in_production_min_32_chars"

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import Base, get_db
from app.main import app
from app.models import Merchant, Payment
from app.security import hash_password, create_access_token


# Test database URL (use in-memory SQLite for testing)
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Create a test client with database override"""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_merchant(db):
    """Create a test merchant"""
    merchant = Merchant(
        email="test@example.com",
        password_hash=hash_password("testpassword123"),
        kyc_verified=False
    )
    db.add(merchant)
    db.commit()
    db.refresh(merchant)
    return merchant


@pytest.fixture
def test_merchant_token(test_merchant):
    """Create a JWT token for test merchant"""
    return create_access_token(subject=test_merchant.email)


@pytest.fixture
def authenticated_client(client, test_merchant_token):
    """Create a test client with authentication"""
    client.headers.update({"Authorization": f"Bearer {test_merchant_token}"})
    return client


@pytest.fixture
def test_payment(db, test_merchant):
    """Create a test payment"""
    from decimal import Decimal
    payment = Payment(
        merchant_id=test_merchant.id,
        amount=Decimal("10.00"),
        currency="XRP",
        status="pending",
        provider="xrp",
        pay_address="rTestAddress123",
        provider_invoice_id="xrp_1_123456"
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment
