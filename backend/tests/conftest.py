"""
Pytest configuration file for shared fixtures and setup
"""
import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture(scope="session")
def test_client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(scope="session")
def admin_credentials():
    """Return admin credentials for testing"""
    return {
        "email": "admin@ksp.gov.in",
        "password": "Admin@123"
    }


@pytest.fixture
def admin_token(test_client, admin_credentials):
    """Get admin authentication token"""
    response = test_client.post("/api/auth/login", json=admin_credentials)
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(admin_token):
    """Get authentication headers with admin token"""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def sample_crime_data():
    """Return sample crime data for testing"""
    return {
        "crime_date": "2024-01-15",
        "district": "Bengaluru Urban",
        "police_station_id": 101,
        "crime_type": "theft",
        "description": "Bike theft near MG Road",
        "status": "open",
        "lat": 12.9716,
        "lng": 77.5946,
        "is_resolved": False
    }


@pytest.fixture
def sample_chat_history():
    """Return sample chat history for testing"""
    return [
        {"role": "user", "content": "Show me theft cases in Bengaluru"},
        {"role": "assistant", "content": "Based on the data, there are 145 theft cases in Bengaluru in the last month."},
        {"role": "user", "content": "What about robbery cases?"},
        {"role": "assistant", "content": "There are 23 robbery cases reported in the same period."}
    ]


@pytest.fixture(autouse=True)
def reset_test_state():
    """Reset any test state before each test"""
    yield
    # Cleanup code here if needed
