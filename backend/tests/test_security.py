from datetime import datetime, timedelta, timezone

import pytest
from app.security import create_access_token, decode_token, hash_password, verify_password


class TestSecurity:
    """Test security utilities"""

    def test_hash_password(self):
        """Test password hashing"""
        password = "testpassword123"
        hashed = hash_password(password)
        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")  # bcrypt prefix

    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        password = "testpassword123"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password"""
        password = "testpassword123"
        hashed = hash_password(password)
        assert verify_password("wrongpassword", hashed) is False

    def test_create_access_token(self):
        """Test JWT token creation"""
        token = create_access_token(subject="test@example.com")
        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_token_valid(self):
        """Test decoding valid token"""
        email = "test@example.com"
        token = create_access_token(subject=email)
        decoded = decode_token(token)
        assert decoded["sub"] == email
        assert "exp" in decoded

    def test_decode_token_invalid(self):
        """Test decoding invalid token"""
        with pytest.raises(Exception):  # Should raise jwt exception
            decode_token("invalid_token")

    def test_token_expiration(self):
        """Test token expiration"""
        import time

        from app.security import create_access_token

        # Create token with 1 second expiration
        token = create_access_token(subject="test@example.com", expires_minutes=0.0001)

        # Wait a bit
        time.sleep(0.1)

        # Should fail to decode
        with pytest.raises(Exception):
            decode_token(token)
