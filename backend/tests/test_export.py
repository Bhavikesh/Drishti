import pytest
from fastapi.testclient import TestClient
from main import app
import io
from PyPDF2 import PdfReader

client = TestClient(app)


@pytest.fixture
def auth_token():
    """Fixture to get authentication token"""
    response = client.post("/api/auth/login", json={
        "email": "admin@ksp.gov.in",
        "password": "Admin@123"
    })
    return response.json()["access_token"]


class TestExport:
    """Test suite for export endpoints"""
    
    def test_pdf_export(self, auth_token):
        """Test PDF report generation"""
        chat_history = [
            {"role": "user", "content": "Show me crimes in Bengaluru"},
            {"role": "assistant", "content": "Based on the data, there are 145 theft cases in Bengaluru in the last month."}
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
        assert "drishti_report.pdf" in response.headers["content-disposition"]
        assert len(response.content) > 0  # PDF has content
    
    def test_pdf_export_content_type(self, auth_token):
        """Test PDF export returns correct content type"""
        response = client.post(
            "/api/export/pdf",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "chat_history": [{"role": "user", "content": "Test"}],
                "user_id": 1,
                "role": "inspector"
            }
        )
        
        assert response.headers["content-type"] == "application/pdf"
    
    def test_pdf_export_with_long_chat(self, auth_token):
        """Test PDF export with lengthy chat history"""
        chat_history = [
            {"role": "user", "content": f"Question {i}"}
            for i in range(50)
        ]
        chat_history.extend([
            {"role": "assistant", "content": f"Answer {i}"}
            for i in range(50)
        ])
        
        response = client.post(
            "/api/export/pdf",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "chat_history": chat_history,
                "user_id": 1,
                "role": "sp"
            }
        )
        
        assert response.status_code == 200
        assert len(response.content) > 1000  # Should be substantial
    
    def test_pdf_export_with_special_characters(self, auth_token):
        """Test PDF export with special characters"""
        chat_history = [
            {"role": "user", "content": "Show cases with symbols: @#$%^&*()"},
            {"role": "assistant", "content": "Here are the results with quotes: \"test\" and 'test'"}
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
    
    def test_pdf_export_empty_chat(self, auth_token):
        """Test PDF export with empty chat history"""
        response = client.post(
            "/api/export/pdf",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "chat_history": [],
                "user_id": 1,
                "role": "constable"
            }
        )
        
        assert response.status_code == 200
        # Should still generate a valid PDF with header
        assert len(response.content) > 0
    
    def test_pdf_export_unauthorized(self):
        """Test PDF export without authentication"""
        response = client.post(
            "/api/export/pdf",
            json={
                "chat_history": [{"role": "user", "content": "Test"}],
                "user_id": 1,
                "role": "admin"
            }
        )
        assert response.status_code == 401
    
    def test_pdf_export_missing_fields(self, auth_token):
        """Test PDF export with missing required fields"""
        response = client.post(
            "/api/export/pdf",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "chat_history": [{"role": "user", "content": "Test"}]
                # Missing user_id and role
            }
        )
        assert response.status_code == 422  # Validation error
    
    def test_pdf_export_invalid_role(self, auth_token):
        """Test PDF export with invalid role"""
        response = client.post(
            "/api/export/pdf",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "chat_history": [{"role": "user", "content": "Test"}],
                "user_id": 1,
                "role": "invalid_role"
            }
        )
        # Should still generate PDF (role is just metadata)
        assert response.status_code in [200, 422]
    
    def test_pdf_export_different_roles(self, auth_token):
        """Test PDF export for different user roles"""
        roles = ["constable", "inspector", "sp", "admin"]
        
        for role in roles:
            response = client.post(
                "/api/export/pdf",
                headers={"Authorization": f"Bearer {auth_token}"},
                json={
                    "chat_history": [
                        {"role": "user", "content": f"Test as {role}"},
                        {"role": "assistant", "content": "Response"}
                    ],
                    "user_id": 1,
                    "role": role
                }
            )
            
            assert response.status_code == 200
            assert len(response.content) > 0
    
    def test_pdf_export_file_size(self, auth_token):
        """Test that PDF has reasonable file size"""
        chat_history = [
            {"role": "user", "content": "Test message"},
            {"role": "assistant", "content": "Test response"}
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
        
        pdf_size = len(response.content)
        assert 500 < pdf_size < 1000000  # Between 500 bytes and 1MB
    
    def test_pdf_export_headers(self, auth_token):
        """Test PDF export response headers"""
        response = client.post(
            "/api/export/pdf",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "chat_history": [{"role": "user", "content": "Test"}],
                "user_id": 1,
                "role": "admin"
            }
        )
        
        assert response.status_code == 200
        assert "content-disposition" in response.headers
        assert "application/pdf" in response.headers["content-type"]
