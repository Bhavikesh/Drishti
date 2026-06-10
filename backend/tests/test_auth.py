import pytest
from fastapi.testclient import TestClient
from main import app
from routes.auth import pwd_context, users_db

client = TestClient(app)


class TestAuthentication:
    """Test suite for authentication endpoints"""
    
    def test_login_success(self):
        """Test successful login with valid credentials"""
        response = client.post("/api/auth/login", json={
            "email": "admin@ksp.gov.in",
            "password": "Admin@123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 20  # JWT tokens are long
    
    def test_login_invalid_password(self):
        """Test login with incorrect password"""
        response = client.post("/api/auth/login", json={
            "email": "admin@ksp.gov.in",
            "password": "WrongPassword123"
        })
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]
    
    def test_login_nonexistent_user(self):
        """Test login with non-existent email"""
        response = client.post("/api/auth/login", json={
            "email": "nonexistent@ksp.gov.in",
            "password": "Password123"
        })
        assert response.status_code == 401
    
    def test_login_invalid_email_format(self):
        """Test login with invalid email format"""
        response = client.post("/api/auth/login", json={
            "email": "not-an-email",
            "password": "Password123"
        })
        assert response.status_code == 422  # Validation error
    
    def test_token_verification(self):
        """Test token verification endpoint"""
        # First login to get token
        login_response = client.post("/api/auth/login", json={
            "email": "admin@ksp.gov.in",
            "password": "Admin@123"
        })
        token = login_response.json()["access_token"]
        
        # Verify token
        response = client.get(
            "/api/auth/verify",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert "user" in data
    
    def test_token_verification_invalid_token(self):
        """Test verification with invalid token"""
        response = client.get(
            "/api/auth/verify",
            headers={"Authorization": "Bearer invalid-token-here"}
        )
        assert response.status_code == 401
    
    def test_token_verification_no_token(self):
        """Test verification without token"""
        response = client.get("/api/auth/verify")
        assert response.status_code == 401
    
    def test_get_current_user(self):
        """Test getting current user profile"""
        # Login first
        login_response = client.post("/api/auth/login", json={
            "email": "admin@ksp.gov.in",
            "password": "Admin@123"
        })
        token = login_response.json()["access_token"]
        
        # Get user profile
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        user_data = response.json()
        assert user_data["email"] == "admin@ksp.gov.in"
        assert user_data["role"] == "admin"
        assert "id" in user_data
    
    def test_get_current_user_unauthorized(self):
        """Test getting profile without authentication"""
        response = client.get("/api/auth/me")
        assert response.status_code == 401
    
    def test_register_user_as_admin(self):
        """Test user registration by admin"""
        # Login as admin
        login_response = client.post("/api/auth/login", json={
            "email": "admin@ksp.gov.in",
            "password": "Admin@123"
        })
        token = login_response.json()["access_token"]
        
        # Register new user
        new_user_email = f"test_inspector_{id(self)}@ksp.gov.in"
        response = client.post(
            "/api/auth/register",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "email": new_user_email,
                "password": "Inspector@123",
                "role": "inspector",
                "assigned_district": "Bengaluru Urban"
            }
        )
        assert response.status_code == 200
        assert "registered successfully" in response.json()["message"].lower()
    
    def test_register_duplicate_email(self):
        """Test registration with duplicate email"""
        # Login as admin
        login_response = client.post("/api/auth/login", json={
            "email": "admin@ksp.gov.in",
            "password": "Admin@123"
        })
        token = login_response.json()["access_token"]
        
        # Try to register with existing email
        response = client.post(
            "/api/auth/register",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "email": "admin@ksp.gov.in",
                "password": "NewPassword123",
                "role": "inspector"
            }
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    def test_register_unauthorized(self):
        """Test registration without admin role"""
        response = client.post("/api/auth/register", json={
            "email": "hacker@evil.com",
            "password": "Password123",
            "role": "admin"
        })
        assert response.status_code == 403
    
    def test_register_invalid_role(self):
        """Test registration with invalid role"""
        # Login as admin
        login_response = client.post("/api/auth/login", json={
            "email": "admin@ksp.gov.in",
            "password": "Admin@123"
        })
        token = login_response.json()["access_token"]
        
        # Try to register with invalid role
        response = client.post(
            "/api/auth/register",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "email": "test@ksp.gov.in",
                "password": "Password123",
                "role": "superuser"  # Invalid role
            }
        )
        assert response.status_code == 422  # Validation error


@pytest.fixture
def admin_token():
    """Fixture to get admin authentication token"""
    response = client.post("/api/auth/login", json={
        "email": "admin@ksp.gov.in",
        "password": "Admin@123"
    })
    return response.json()["access_token"]


def test_password_hashing():
    """Test that passwords are properly hashed"""
    password = "TestPassword123"
    hashed = pwd_context.hash(password)
    
    # Hash should be different from original
    assert hashed != password
    # Should be able to verify
    assert pwd_context.verify(password, hashed)
    # Wrong password should fail
    assert not pwd_context.verify("WrongPassword", hashed)
