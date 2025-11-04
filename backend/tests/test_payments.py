from unittest.mock import MagicMock, patch

import pytest
from fastapi import status


class TestPayments:
    """Test payment endpoints"""

    def test_create_xrp_payment_success(self, authenticated_client, test_merchant):
        """Test successful XRP payment creation"""
        with (
            patch("app.routers.payments.convert_usd_to_xrp") as mock_convert,
            patch("app.routers.payments.generate_xrp_payment_address") as mock_addr,
            patch("app.config.settings") as mock_settings,
        ):

            from decimal import Decimal

            mock_settings.XRP_WALLET_ADDRESS = "rTestWallet123"
            mock_convert.return_value = Decimal("50.0")
            mock_addr.return_value = {"address": "rTestWallet123", "destination_tag": 123456, "amount_xrp": None}

            response = authenticated_client.post("/api/payments", json={"amount": 10.00, "currency": "XRP"})

            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["status"] == "pending"
            assert data["payment_id"] > 0
            assert data["pay_address"] == "rTestWallet123"
            assert "xrp_" in data["provider_invoice_id"]

    def test_create_xrp_payment_no_wallet(self, authenticated_client):
        """Test XRP payment creation without wallet configured"""
        with patch("app.config.settings") as mock_settings:
            mock_settings.XRP_WALLET_ADDRESS = ""

            response = authenticated_client.post("/api/payments", json={"amount": 10.00, "currency": "XRP"})

            assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE

    def test_create_payment_invalid_currency(self, authenticated_client):
        """Test payment creation with unsupported currency"""
        response = authenticated_client.post("/api/payments", json={"amount": 10.00, "currency": "INVALID"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "unsupported currency" in response.json()["detail"].lower()

    def test_create_payment_invalid_amount(self, authenticated_client):
        """Test payment creation with invalid amount"""
        response = authenticated_client.post("/api/payments", json={"amount": -10.00, "currency": "XRP"})
        # Should fail validation or business logic
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]

    def test_create_payment_unauthorized(self, client):
        """Test payment creation without authentication"""
        response = client.post("/api/payments", json={"amount": 10.00, "currency": "XRP"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_payment_success(self, authenticated_client, test_merchant, test_payment):
        """Test getting payment details"""
        response = authenticated_client.get(f"/api/payments/{test_payment.id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_payment.id
        assert data["amount"] == float(test_payment.amount)
        assert data["currency"] == test_payment.currency
        assert data["status"] == test_payment.status

    def test_get_payment_not_found(self, authenticated_client):
        """Test getting non-existent payment"""
        response = authenticated_client.get("/api/payments/99999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_payment_other_merchant(self, client, db, test_merchant):
        """Test getting payment from different merchant (should fail)"""
        from decimal import Decimal

        from app.models import Merchant, Payment
        from app.security import create_access_token, hash_password

        # Create another merchant
        other_merchant = Merchant(
            email="other@example.com", password_hash=hash_password("password123"), kyc_verified=False
        )
        db.add(other_merchant)
        db.commit()
        db.refresh(other_merchant)

        # Create payment for other merchant
        other_payment = Payment(
            merchant_id=other_merchant.id,
            amount=Decimal("20.00"),
            currency="BTC",
            status="pending",
            provider="nowpayments",
        )
        db.add(other_payment)
        db.commit()
        db.refresh(other_payment)

        # Try to access with test_merchant token
        token = create_access_token(subject=test_merchant.email)
        client.headers.update({"Authorization": f"Bearer {token}"})

        response = client.get(f"/api/payments/{other_payment.id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @patch("app.routers.payments.create_nowpayments_invoice")
    def test_create_nowpayments_payment(self, mock_invoice, authenticated_client):
        """Test creating payment via NOWPayments"""
        mock_invoice.return_value = {
            "payment_id": "nowpay_123",
            "pay_address": "bc1test123",
            "invoice_url": "https://nowpayments.io/pay/123",
        }

        response = authenticated_client.post("/api/payments", json={"amount": 10.00, "currency": "BTC"})

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["status"] == "pending"
        assert data["pay_address"] == "bc1test123"
