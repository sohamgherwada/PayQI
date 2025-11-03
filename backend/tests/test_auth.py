import pytest
from fastapi import status


class TestAuth:
    """Test authentication endpoints"""

    def test_register_success(self, client):
        """Test successful merchant registration"""
        response = client.post(
            "/api/register",
            json={
                "email": "newmerchant@example.com",
                "password": "securepass123"
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == "newmerchant@example.com"
        assert "id" in data
        assert data["kyc_verified"] is False
        assert "password" not in str(data)

    def test_register_duplicate_email(self, client, test_merchant):
        """Test registration with duplicate email"""
        response = client.post(
            "/api/register",
            json={
                "email": test_merchant.email,
                "password": "anotherpassword123"
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in response.json()["detail"].lower()

    def test_register_invalid_email(self, client):
        """Test registration with invalid email"""
        response = client.post(
            "/api/register",
            json={
                "email": "notanemail",
                "password": "password123"
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_short_password(self, client):
        """Test registration with password too short"""
        response = client.post(
            "/api/register",
            json={
                "email": "test@example.com",
                "password": "short"  # Less than 8 characters
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_login_success(self, client, test_merchant):
        """Test successful login"""
        response = client.post(
            "/api/login",
            json={
                "email": test_merchant.email,
                "password": "testpassword123"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0

    def test_login_invalid_email(self, client):
        """Test login with non-existent email"""
        response = client.post(
            "/api/login",
            json={
                "email": "nonexistent@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "invalid" in response.json()["detail"].lower()

    def test_login_invalid_password(self, client, test_merchant):
        """Test login with wrong password"""
        response = client.post(
            "/api/login",
            json={
                "email": test_merchant.email,
                "password": "wrongpassword"
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "invalid" in response.json()["detail"].lower()

    def test_get_me_success(self, authenticated_client, test_merchant):
        """Test getting current merchant info"""
        response = authenticated_client.get("/api/me")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == test_merchant.email
        assert data["id"] == test_merchant.id

    def test_get_me_unauthorized(self, client):
        """Test getting merchant info without authentication"""
        response = client.get("/api/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_me_invalid_token(self, client):
        """Test getting merchant info with invalid token"""
        client.headers.update({"Authorization": "Bearer invalid_token"})
        response = client.get("/api/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
