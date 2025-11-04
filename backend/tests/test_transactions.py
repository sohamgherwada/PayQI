"""Tests for transaction endpoints"""
import pytest
from unittest.mock import patch, AsyncMock


@pytest.fixture
def authenticated_client(client):
    """Create a client with authenticated user"""
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


def test_get_transactions_empty(authenticated_client):
    """Test getting transactions when none exist"""
    response = authenticated_client.get("/api/transactions")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []


def test_get_transactions(authenticated_client):
    """Test getting all transactions"""
    mock_response = {
        "payment_id": "test_payment_123",
        "pay_address": "rXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        "invoice_url": "https://nowpayments.io/checkout/test"
    }
    
    with patch("app.routers.payments.create_nowpayments_invoice", new_callable=AsyncMock) as mock_invoice:
        mock_invoice.return_value = mock_response
        
        # Create multiple payments
        authenticated_client.post("/api/payments", json={"amount": 10.50, "currency": "xrp"})
        authenticated_client.post("/api/payments", json={"amount": 20.00, "currency": "btc"})
        
        # Get transactions
        response = authenticated_client.get("/api/transactions")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        # Should be ordered by created_at desc (newest first)
        assert data["items"][0]["amount"] == 20.00
        assert data["items"][1]["amount"] == 10.50
