"""Tests for authentication endpoints"""


def test_register_merchant(client):
    """Test merchant registration"""
    response = client.post(
        "/api/register",
        json={"email": "test@example.com", "password": "testpass123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert data["kyc_verified"] is False


def test_register_duplicate_email(client):
    """Test registration with duplicate email"""
    client.post(
        "/api/register",
        json={"email": "test@example.com", "password": "testpass123"}
    )
    response = client.post(
        "/api/register",
        json={"email": "test@example.com", "password": "testpass123"}
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_login_success(client):
    """Test successful login"""
    client.post(
        "/api/register",
        json={"email": "test@example.com", "password": "testpass123"}
    )
    response = client.post(
        "/api/login",
        json={"email": "test@example.com", "password": "testpass123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client):
    """Test login with invalid credentials"""
    response = client.post(
        "/api/login",
        json={"email": "test@example.com", "password": "wrongpass"}
    )
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]


def test_get_me(client):
    """Test getting current user"""
    # Register
    client.post(
        "/api/register",
        json={"email": "test@example.com", "password": "testpass123"}
    )
    # Login
    login_response = client.post(
        "/api/login",
        json={"email": "test@example.com", "password": "testpass123"}
    )
    token = login_response.json()["access_token"]
    
    # Get me
    response = client.get(
        "/api/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"


def test_get_me_unauthorized(client):
    """Test getting current user without token"""
    response = client.get("/api/me")
    assert response.status_code == 401
