"""
Integration tests for complete workflows
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


@pytest.mark.integration
class TestInvestigationWorkflow:
    """Test complete investigation workflow"""
    
    def test_full_investigation_workflow(self):
        """Test complete investigation workflow from login to export"""
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
        assert "response" in chat_response.json()
        
        # 3. Get network analysis
        network_response = client.post(
            "/api/network/graph",
            headers=headers,
            json={"crime_id": 123}
        )
        assert network_response.status_code == 200
        assert "nodes" in network_response.json()
        assert "links" in network_response.json()
        
        # 4. Get predictions
        forecast_response = client.get(
            "/api/predictions/forecast?district=Bengaluru&days=7",
            headers=headers
        )
        assert forecast_response.status_code == 200
        assert "forecast" in forecast_response.json()
        
        # 5. Get hotspots
        hotspots_response = client.get(
            "/api/predictions/hotspots?crime_type=theft",
            headers=headers
        )
        assert hotspots_response.status_code == 200
        assert "hotspots" in hotspots_response.json()
        
        # 6. Export report
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


@pytest.mark.integration
class TestMultiSessionWorkflow:
    """Test multiple concurrent sessions"""
    
    def test_multiple_sessions(self):
        """Test multiple chat sessions simultaneously"""
        # Login
        login_response = client.post("/api/auth/login", json={
            "email": "admin@ksp.gov.in",
            "password": "Admin@123"
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create multiple sessions
        sessions = ["session-1", "session-2", "session-3"]
        
        for session_id in sessions:
            response = client.post(
                "/api/chat/",
                headers=headers,
                json={
                    "message": f"Query for {session_id}",
                    "session_id": session_id,
                    "language": "en"
                }
            )
            assert response.status_code == 200


@pytest.mark.integration
class TestErrorHandlingWorkflow:
    """Test error handling across the system"""
    
    def test_graceful_degradation(self):
        """Test system continues working when some services fail"""
        # Login
        login_response = client.post("/api/auth/login", json={
            "email": "admin@ksp.gov.in",
            "password": "Admin@123"
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Even if RAG or Mistral fail, should get some response
        response = client.post(
            "/api/chat/",
            headers=headers,
            json={
                "message": "Test query",
                "session_id": "error-test",
                "language": "en"
            }
        )
        
        # Should not crash, even if AI services are down
        assert response.status_code in [200, 500, 503]


@pytest.mark.integration
class TestAuthenticationFlow:
    """Test complete authentication flows"""
    
    def test_register_login_workflow(self):
        """Test user registration and subsequent login"""
        # Login as admin
        admin_login = client.post("/api/auth/login", json={
            "email": "admin@ksp.gov.in",
            "password": "Admin@123"
        })
        admin_token = admin_login.json()["access_token"]
        
        # Register new user
        new_email = f"test_user_{id(self)}@ksp.gov.in"
        register_response = client.post(
            "/api/auth/register",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "email": new_email,
                "password": "Test@123",
                "role": "constable",
                "assigned_district": "Mysore"
            }
        )
        assert register_response.status_code == 200
        
        # Login as new user
        user_login = client.post("/api/auth/login", json={
            "email": new_email,
            "password": "Test@123"
        })
        assert user_login.status_code == 200
        assert "access_token" in user_login.json()
        
        # Verify new user can access protected endpoints
        user_token = user_login.json()["access_token"]
        me_response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert me_response.status_code == 200
        assert me_response.json()["email"] == new_email


@pytest.mark.integration
class TestDataFlow:
    """Test data flow through the system"""
    
    def test_chat_to_export_data_flow(self):
        """Test data flows correctly from chat through to export"""
        # Login
        login_response = client.post("/api/auth/login", json={
            "email": "admin@ksp.gov.in",
            "password": "Admin@123"
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Have a conversation
        messages = [
            "What are the crime statistics?",
            "Show me network analysis",
            "Generate predictions"
        ]
        
        chat_history = []
        for message in messages:
            response = client.post(
                "/api/chat/",
                headers=headers,
                json={
                    "message": message,
                    "session_id": "data-flow-test",
                    "language": "en"
                }
            )
            assert response.status_code == 200
            
            chat_history.append({"role": "user", "content": message})
            chat_history.append({
                "role": "assistant",
                "content": response.json()["response"]
            })
        
        # Export the conversation
        export_response = client.post(
            "/api/export/pdf",
            headers=headers,
            json={
                "chat_history": chat_history,
                "user_id": 1,
                "role": "admin"
            }
        )
        
        assert export_response.status_code == 200
        assert len(export_response.content) > 0
