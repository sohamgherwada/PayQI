"""Tests for payment endpoints"""
import pytest
from unittest.mock import patch, AsyncMock


@pytest.fixture
def authenticated_client(client):
    """Create a client with authenticated user"""
    # Register and login
    client.post(
        "/api/register",
        json={"email": "merchant@example.com", "password": "testpass123"}
    )
    login_response = client.post(
        "/api/login",
        json={"email": "merchant@example.com", "password": "testpass123"}
    )
    token = login_response.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token}"}
    return client


def test_create_payment_xrp(authenticated_client):
    """Test creating XRP payment"""
    mock_response = {
        "payment_id": "test_payment_123",
        "pay_address": "rXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        "invoice_url": "https://nowpayments.io/checkout/test"
    }
    
    with patch("app.routers.payments.create_nowpayments_invoice", new_callable=AsyncMock) as mock_invoice:
        mock_invoice.return_value = mock_response
        
        response = authenticated_client.post(
            "/api/payments",
            json={"amount": 10.50, "currency": "xrp"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "pending"
        assert "payment_id" in data
        assert data["pay_address"] == "rXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"


def test_create_payment_unsupported_currency(authenticated_client):
    """Test creating payment with unsupported currency"""
    response = authenticated_client.post(
        "/api/payments",
        json={"amount": 10.50, "currency": "invalid_coin"}
    )
    
    assert response.status_code == 400
    assert "not supported" in response.json()["detail"].lower()


def test_create_payment_case_insensitive_currency(authenticated_client):
    """Test currency is case insensitive"""
    mock_response = {
        "payment_id": "test_payment_123",
        "pay_address": "rXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        "invoice_url": "https://nowpayments.io/checkout/test"
    }
    
    with patch("app.routers.payments.create_nowpayments_invoice", new_callable=AsyncMock) as mock_invoice:
        mock_invoice.return_value = mock_response
        
        # Test uppercase
        response = authenticated_client.post(
            "/api/payments",
            json={"amount": 10.50, "currency": "XRP"}
        )
        assert response.status_code == 200
        
        # Test mixed case
        response = authenticated_client.post(
            "/api/payments",
            json={"amount": 10.50, "currency": "Btc"}
        )
        assert response.status_code == 200


def test_get_payment(authenticated_client):
    """Test getting payment details"""
    mock_response = {
        "payment_id": "test_payment_123",
        "pay_address": "rXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        "invoice_url": "https://nowpayments.io/checkout/test"
    }
    
    with patch("app.routers.payments.create_nowpayments_invoice", new_callable=AsyncMock) as mock_invoice:
        mock_invoice.return_value = mock_response
        
        # Create payment
        create_response = authenticated_client.post(
            "/api/payments",
            json={"amount": 10.50, "currency": "xrp"}
        )
        payment_id = create_response.json()["payment_id"]
        
        # Get payment
        response = authenticated_client.get(f"/api/payments/{payment_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == payment_id
        assert data["currency"] == "xrp"
        assert data["amount"] == 10.50


def test_get_payment_not_found(authenticated_client):
    """Test getting non-existent payment"""
    response = authenticated_client.get("/api/payments/99999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
