import pytest
from fastapi import status
from decimal import Decimal


class TestTransactions:
    """Test transaction endpoints"""

    def test_get_transactions_success(self, authenticated_client, db, test_merchant):
        """Test getting transactions"""
        from app.models import Payment

        # Create multiple payments
        for i in range(3):
            payment = Payment(
                merchant_id=test_merchant.id,
                amount=Decimal(f"{10 + i}.00"),
                currency="XRP",
                status="pending" if i % 2 == 0 else "completed",
                provider="xrp",
            )
            db.add(payment)
        db.commit()

        response = authenticated_client.get("/api/transactions")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert len(data["items"]) == 3
        assert all("amount" in item for item in data["items"])

    def test_get_transactions_empty(self, authenticated_client):
        """Test getting transactions when none exist"""
        response = authenticated_client.get("/api/transactions")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert len(data["items"]) == 0

    def test_get_transactions_pagination(self, authenticated_client, db, test_merchant):
        """Test transaction pagination"""
        from app.models import Payment

        # Create 5 payments
        for i in range(5):
            payment = Payment(
                merchant_id=test_merchant.id, amount=Decimal("10.00"), currency="XRP", status="pending", provider="xrp"
            )
            db.add(payment)
        db.commit()

        # Get first 2
        response = authenticated_client.get("/api/transactions?skip=0&limit=2")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) == 2

        # Get next 2
        response = authenticated_client.get("/api/transactions?skip=2&limit=2")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) == 2

    def test_get_transactions_unauthorized(self, client):
        """Test getting transactions without authentication"""
        response = client.get("/api/transactions")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_transactions_only_own(self, client, db, test_merchant):
        """Test that merchants only see their own transactions"""
        from app.models import Merchant, Payment
        from app.security import hash_password, create_access_token
        from decimal import Decimal

        # Create another merchant with payment
        other_merchant = Merchant(
            email="other@example.com", password_hash=hash_password("password123"), kyc_verified=False
        )
        db.add(other_merchant)

        other_payment = Payment(
            merchant_id=other_merchant.id,
            amount=Decimal("100.00"),
            currency="BTC",
            status="completed",
            provider="nowpayments",
        )
        db.add(other_payment)
        db.commit()

        # Create payment for test_merchant
        my_payment = Payment(
            merchant_id=test_merchant.id, amount=Decimal("50.00"), currency="XRP", status="pending", provider="xrp"
        )
        db.add(my_payment)
        db.commit()

        # Get transactions for test_merchant
        token = create_access_token(subject=test_merchant.email)
        client.headers.update({"Authorization": f"Bearer {token}"})

        response = client.get("/api/transactions")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Should only see own payment
        assert len(data["items"]) == 1
        assert data["items"][0]["amount"] == 50.0
