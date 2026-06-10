# 🧪 Testing Documentation

This document provides comprehensive testing guidelines for the Drishti AI platform.

## Table of Contents
- [Testing Strategy](#testing-strategy)
- [Backend Testing](#backend-testing)
- [Frontend Testing](#frontend-testing)
- [Integration Testing](#integration-testing)
- [Performance Testing](#performance-testing)
- [Security Testing](#security-testing)

## Testing Strategy

### Test Pyramid
```
                    ▲
                   / \
                  /E2E\
                 /_____\
                /       \
               /  INTE   \
              /  GRATION  \
             /_____________\
            /               \
           /   UNIT TESTS    \
          /__________________\
```

- **70% Unit Tests**: Test individual functions and components
- **20% Integration Tests**: Test API endpoints and data flow
- **10% E2E Tests**: Test complete user workflows

### Test Coverage Goals
- Overall coverage: **> 80%**
- Critical paths: **> 95%**
- Security modules: **100%**

## Backend Testing

### Setup

```bash
cd backend

# Install test dependencies
pip install pytest pytest-cov pytest-asyncio httpx faker

# Create test configuration
export TESTING=true
export DATABASE_URL=postgresql://test:test@localhost:5432/drishti_test
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=. --cov-report=html

# Run specific test file
pytest tests/test_chat.py -v

# Run specific test
pytest tests/test_chat.py::test_chat_endpoint -v

# Run with markers
pytest -m "not slow" -v
```

### Unit Tests

#### Authentication Tests

**File:** `tests/test_auth.py`

```python
import pytest
from fastapi.testclient import TestClient
from main import app
from routes.auth import pwd_context, users_db

client = TestClient(app)

def test_login_success():
    """Test successful login"""
    response = client.post("/api/auth/login", json={
        "email": "admin@ksp.gov.in",
        "password": "Admin@123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_invalid_credentials():
    """Test login with invalid credentials"""
    response = client.post("/api/auth/login", json={
        "email": "admin@ksp.gov.in",
        "password": "WrongPassword"
    })
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]

def test_login_nonexistent_user():
    """Test login with non-existent user"""
    response = client.post("/api/auth/login", json={
        "email": "fake@ksp.gov.in",
        "password": "Password123"
    })
    assert response.status_code == 401

def test_token_verification():
    """Test token verification endpoint"""
    # First login
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
    assert response.json()["valid"] is True

def test_get_current_user():
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
    assert response.json()["email"] == "admin@ksp.gov.in"
    assert response.json()["role"] == "admin"

def test_register_user_as_admin():
    """Test user registration by admin"""
    # Login as admin
    login_response = client.post("/api/auth/login", json={
        "email": "admin@ksp.gov.in",
        "password": "Admin@123"
    })
    token = login_response.json()["access_token"]
    
    # Register new user
    response = client.post(
        "/api/auth/register",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "email": "inspector@ksp.gov.in",
            "password": "Inspector@123",
            "role": "inspector",
            "assigned_district": "Bengaluru Urban"
        }
    )
    assert response.status_code == 200
    assert "registered successfully" in response.json()["message"]

def test_register_unauthorized():
    """Test registration without admin role"""
    response = client.post("/api/auth/register", json={
        "email": "hacker@evil.com",
        "password": "Password123",
        "role": "admin"
    })
    assert response.status_code == 403
```

#### Chat Endpoint Tests

**File:** `tests/test_chat.py`

```python
import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, MagicMock

client = TestClient(app)

@pytest.fixture
def auth_token():
    """Fixture to get authentication token"""
    response = client.post("/api/auth/login", json={
        "email": "admin@ksp.gov.in",
        "password": "Admin@123"
    })
    return response.json()["access_token"]

def test_chat_endpoint_unauthorized():
    """Test chat endpoint without authentication"""
    response = client.post("/api/chat/", json={
        "message": "Show me crimes",
        "session_id": "test-session",
        "language": "en"
    })
    assert response.status_code == 401

@patch('rag_pipeline.retrieve_relevant_crimes')
@patch('mistral_client.query_mistral')
def test_chat_endpoint_success(mock_mistral, mock_rag, auth_token):
    """Test successful chat interaction"""
    # Mock RAG response
    mock_rag.return_value = {
        'documents': [["Crime 1 details", "Crime 2 details"]],
        'metadatas': [[{"case_id": "C001"}, {"case_id": "C002"}]]
    }
    
    # Mock Mistral response
    mock_mistral.return_value = "Based on the data, there are 2 relevant crimes."
    
    response = client.post(
        "/api/chat/",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "message": "Show me theft cases",
            "session_id": "test-session-123",
            "language": "en"
        }
    )
    
    assert response.status_code == 200
    assert "response" in response.json()
    assert "sources" in response.json()
    assert "confidence" in response.json()

@patch('translation.translate_to_english')
@patch('translation.translate_to_kannada')
@patch('mistral_client.query_mistral')
def test_chat_kannada_translation(mock_mistral, mock_to_kannada, mock_to_english, auth_token):
    """Test chat with Kannada language"""
    mock_to_english.return_value = "Show me crimes"
    mock_mistral.return_value = "Here are the crimes"
    mock_to_kannada.return_value = "ಇಲ್ಲಿ ಅಪರಾಧಗಳಿವೆ"
    
    response = client.post(
        "/api/chat/",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "message": "ಅಪರಾಧಗಳನ್ನು ತೋರಿಸಿ",
            "session_id": "test-session-kn",
            "language": "kn"
        }
    )
    
    assert response.status_code == 200
    # Should return Kannada response
    assert mock_to_kannada.called

def test_chat_session_management(auth_token):
    """Test that chat maintains session context"""
    session_id = "test-session-context"
    
    # First message
    response1 = client.post(
        "/api/chat/",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "message": "What are theft statistics?",
            "session_id": session_id,
            "language": "en"
        }
    )
    assert response1.status_code == 200
    
    # Second message in same session
    response2 = client.post(
        "/api/chat/",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "message": "What about in Bengaluru?",
            "session_id": session_id,
            "language": "en"
        }
    )
    assert response2.status_code == 200
```

#### Network Analysis Tests

**File:** `tests/test_network.py`

```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.fixture
def auth_token():
    response = client.post("/api/auth/login", json={
        "email": "admin@ksp.gov.in",
        "password": "Admin@123"
    })
    return response.json()["access_token"]

def test_network_graph_endpoint(auth_token):
    """Test network graph generation"""
    response = client.post(
        "/api/network/graph",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"crime_id": 123}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "links" in data
    assert isinstance(data["nodes"], list)
    assert isinstance(data["links"], list)

def test_network_graph_structure(auth_token):
    """Test network graph data structure"""
    response = client.post(
        "/api/network/graph",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"criminal_name": "Test Criminal"}
    )
    
    data = response.json()
    
    # Check node structure
    if len(data["nodes"]) > 0:
        node = data["nodes"][0]
        assert "id" in node
        assert "name" in node
        assert "crimeCount" in node
    
    # Check link structure
    if len(data["links"]) > 0:
        link = data["links"][0]
        assert "source" in link
        assert "target" in link
```

#### Predictions Tests

**File:** `tests/test_predictions.py`

```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.fixture
def auth_token():
    response = client.post("/api/auth/login", json={
        "email": "admin@ksp.gov.in",
        "password": "Admin@123"
    })
    return response.json()["access_token"]

def test_forecast_endpoint(auth_token):
    """Test crime forecast generation"""
    response = client.get(
        "/api/predictions/forecast?district=Bengaluru&days=30",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "district" in data
    assert "forecast" in data
    assert data["district"] == "Bengaluru"

def test_hotspots_endpoint(auth_token):
    """Test crime hotspots identification"""
    response = client.get(
        "/api/predictions/hotspots?crime_type=theft",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "crime_type" in data
    assert "hotspots" in data
    assert isinstance(data["hotspots"], list)
    
    # Check hotspot structure
    if len(data["hotspots"]) > 0:
        hotspot = data["hotspots"][0]
        assert "station" in hotspot
        assert "count" in hotspot
        assert "lat" in hotspot
        assert "lng" in hotspot

def test_alerts_endpoint(auth_token):
    """Test predictive alerts"""
    response = client.get(
        "/api/predictions/alerts",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "alerts" in data
    assert isinstance(data["alerts"], list)
```

#### Export Tests

**File:** `tests/test_export.py`

```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.fixture
def auth_token():
    response = client.post("/api/auth/login", json={
        "email": "admin@ksp.gov.in",
        "password": "Admin@123"
    })
    return response.json()["access_token"]

def test_pdf_export(auth_token):
    """Test PDF report generation"""
    chat_history = [
        {"role": "user", "content": "Show me crimes in Bengaluru"},
        {"role": "assistant", "content": "Here are the crimes..."}
    ]
    
    response = client.post(
        "/api/export/pdf",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "chat_history": chat_history,
            "user_id": 1,
            "role": "admin"
        }
    )
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert "attachment" in response.headers["content-disposition"]
    assert len(response.content) > 0  # PDF has content
```

### Integration Tests

**File:** `tests/test_integration.py`

```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_full_investigation_workflow():
    """Test complete investigation workflow"""
    # 1. Login
    login_response = client.post("/api/auth/login", json={
        "email": "admin@ksp.gov.in",
        "password": "Admin@123"
    })
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Query crimes via chat
    chat_response = client.post(
        "/api/chat/",
        headers=headers,
        json={
            "message": "Show me theft cases in Bengaluru",
            "session_id": "investigation-001",
            "language": "en"
        }
    )
    assert chat_response.status_code == 200
    
    # 3. Get network analysis
    network_response = client.post(
        "/api/network/graph",
        headers=headers,
        json={"crime_id": 123}
    )
    assert network_response.status_code == 200
    
    # 4. Get predictions
    forecast_response = client.get(
        "/api/predictions/forecast?district=Bengaluru&days=7",
        headers=headers
    )
    assert forecast_response.status_code == 200
    
    # 5. Export report
    export_response = client.post(
        "/api/export/pdf",
        headers=headers,
        json={
            "chat_history": [
                {"role": "user", "content": "Show me theft cases"},
                {"role": "assistant", "content": chat_response.json()["response"]}
            ],
            "user_id": 1,
            "role": "admin"
        }
    )
    assert export_response.status_code == 200
    assert export_response.headers["content-type"] == "application/pdf"
```

### Rate Limiting Tests

**File:** `tests/test_rate_limiting.py`

```python
import pytest
from fastapi.testclient import TestClient
from main import app
import time

client = TestClient(app)

@pytest.fixture
def auth_token():
    response = client.post("/api/auth/login", json={
        "email": "admin@ksp.gov.in",
        "password": "Admin@123"
    })
    return response.json()["access_token"]

def test_rate_limiting(auth_token):
    """Test that rate limiting prevents excessive requests"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Make multiple rapid requests
    responses = []
    for i in range(150):  # Assuming limit is 100/minute
        response = client.post(
            "/api/chat/",
            headers=headers,
            json={
                "message": f"Test message {i}",
                "session_id": "rate-test",
                "language": "en"
            }
        )
        responses.append(response.status_code)
        if response.status_code == 429:
            break
    
    # Should get rate limited
    assert 429 in responses
```

## Frontend Testing

### Setup

```bash
cd frontend

# Install test dependencies
npm install --save-dev @testing-library/react @testing-library/jest-dom @testing-library/user-event vitest jsdom
```

### Component Tests

**File:** `src/components/Chat.test.tsx`

```typescript
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Chat } from './Chat';

describe('Chat Component', () => {
  it('renders chat interface', () => {
    render(<Chat />);
    expect(screen.getByPlaceholderText(/type your message/i)).toBeInTheDocument();
  });

  it('sends message on submit', async () => {
    const mockSend = vi.fn();
    render(<Chat onSendMessage={mockSend} />);
    
    const input = screen.getByPlaceholderText(/type your message/i);
    const sendButton = screen.getByRole('button', { name: /send/i });
    
    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.click(sendButton);
    
    await waitFor(() => {
      expect(mockSend).toHaveBeenCalledWith('Test message');
    });
  });
});
```

## Performance Testing

### Load Testing with Locust

**File:** `tests/load_test.py`

```python
from locust import HttpUser, task, between

class DrishtiUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Login before starting tests"""
        response = self.client.post("/api/auth/login", json={
            "email": "admin@ksp.gov.in",
            "password": "Admin@123"
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    @task(3)
    def chat_query(self):
        self.client.post(
            "/api/chat/",
            headers=self.headers,
            json={
                "message": "Show me crimes",
                "session_id": "load-test",
                "language": "en"
            }
        )
    
    @task(1)
    def get_forecast(self):
        self.client.get(
            "/api/predictions/forecast",
            headers=self.headers
        )
    
    @task(1)
    def get_network(self):
        self.client.post(
            "/api/network/graph",
            headers=self.headers,
            json={"crime_id": 123}
        )

# Run with: locust -f tests/load_test.py --host=http://localhost:8000
```

## Security Testing

### SQL Injection Tests
```python
def test_sql_injection_protection(auth_token):
    """Test protection against SQL injection"""
    malicious_inputs = [
        "'; DROP TABLE users; --",
        "1' OR '1'='1",
        "admin'--",
    ]
    
    for payload in malicious_inputs:
        response = client.post(
            "/api/chat/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "message": payload,
                "session_id": "security-test",
                "language": "en"
            }
        )
        # Should not cause server error
        assert response.status_code in [200, 400, 422]
```

### XSS Protection Tests
```python
def test_xss_protection(auth_token):
    """Test protection against XSS attacks"""
    xss_payload = "<script>alert('XSS')</script>"
    
    response = client.post(
        "/api/chat/",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "message": xss_payload,
            "session_id": "xss-test",
            "language": "en"
        }
    )
    
    # Script should be sanitized in response
    assert "<script>" not in response.text
```

## Test Coverage Report

```bash
# Generate coverage report
cd backend
pytest tests/ --cov=. --cov-report=html --cov-report=term

# Open HTML report
# On Windows: start htmlcov/index.html
# On Linux: xdg-open htmlcov/index.html
```

## Continuous Integration

**File:** `.github/workflows/test.yml`

```yaml
name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: |
          cd backend
          pytest tests/ -v --cov
  
  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Node
        uses: actions/setup-node@v2
        with:
          node-version: '18'
      - name: Install dependencies
        run: |
          cd frontend
          npm install
      - name: Run tests
        run: |
          cd frontend
          npm run test
```

## Best Practices

1. **Write tests first** (TDD approach)
2. **Keep tests independent** - each test should run in isolation
3. **Use fixtures** for common setup
4. **Mock external services** (Mistral AI, databases)
5. **Test edge cases** and error conditions
6. **Maintain high coverage** (>80%)
7. **Run tests before commits**
8. **Document complex test scenarios**

---

For questions or issues with testing, contact the development team.
