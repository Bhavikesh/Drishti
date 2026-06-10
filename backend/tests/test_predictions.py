import pytest
from fastapi.testclient import TestClient
from main import app
from datetime import datetime

client = TestClient(app)


@pytest.fixture
def auth_token():
    """Fixture to get authentication token"""
    response = client.post("/api/auth/login", json={
        "email": "admin@ksp.gov.in",
        "password": "Admin@123"
    })
    return response.json()["access_token"]


class TestPredictions:
    """Test suite for prediction endpoints"""
    
    def test_forecast_endpoint(self, auth_token):
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
        assert isinstance(data["forecast"], list)
    
    def test_forecast_default_parameters(self, auth_token):
        """Test forecast with default parameters"""
        response = client.get(
            "/api/predictions/forecast",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "district" in data
        assert "forecast" in data
    
    def test_forecast_custom_days(self, auth_token):
        """Test forecast with custom number of days"""
        days = 7
        response = client.get(
            f"/api/predictions/forecast?days={days}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "forecast" in data
        # Forecast should have approximately the requested number of days
        assert len(data["forecast"]) <= days + 5  # Allow some flexibility
    
    def test_forecast_data_structure(self, auth_token):
        """Test forecast data structure"""
        response = client.get(
            "/api/predictions/forecast?days=7",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        data = response.json()
        
        if len(data["forecast"]) > 0:
            forecast_item = data["forecast"][0]
            assert "ds" in forecast_item  # Date/timestamp
            assert "yhat" in forecast_item  # Prediction
            assert "yhat_lower" in forecast_item  # Lower bound
            assert "yhat_upper" in forecast_item  # Upper bound
    
    def test_forecast_unauthorized(self):
        """Test forecast without authentication"""
        response = client.get("/api/predictions/forecast")
        assert response.status_code == 401
    
    def test_hotspots_endpoint(self, auth_token):
        """Test crime hotspots identification"""
        response = client.get(
            "/api/predictions/hotspots?crime_type=theft",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "crime_type" in data
        assert "hotspots" in data
        assert data["crime_type"] == "theft"
        assert isinstance(data["hotspots"], list)
    
    def test_hotspots_default_crime_type(self, auth_token):
        """Test hotspots with default crime type"""
        response = client.get(
            "/api/predictions/hotspots",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "crime_type" in data
        assert "hotspots" in data
    
    def test_hotspots_data_structure(self, auth_token):
        """Test hotspots data structure"""
        response = client.get(
            "/api/predictions/hotspots",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        data = response.json()
        
        # Check hotspot structure
        if len(data["hotspots"]) > 0:
            hotspot = data["hotspots"][0]
            assert "station" in hotspot
            assert "count" in hotspot
            assert "lat" in hotspot
            assert "lng" in hotspot
            
            # Validate data types
            assert isinstance(hotspot["station"], str)
            assert isinstance(hotspot["count"], int)
            assert isinstance(hotspot["lat"], (int, float))
            assert isinstance(hotspot["lng"], (int, float))
            
            # Validate coordinate ranges
            assert -90 <= hotspot["lat"] <= 90
            assert -180 <= hotspot["lng"] <= 180
    
    def test_hotspots_sorted_by_count(self, auth_token):
        """Test that hotspots are sorted by crime count"""
        response = client.get(
            "/api/predictions/hotspots",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        data = response.json()
        hotspots = data["hotspots"]
        
        if len(hotspots) > 1:
            # Check if sorted in descending order by count
            counts = [h["count"] for h in hotspots]
            assert counts == sorted(counts, reverse=True), "Hotspots should be sorted by count"
    
    def test_hotspots_unauthorized(self):
        """Test hotspots without authentication"""
        response = client.get("/api/predictions/hotspots")
        assert response.status_code == 401
    
    def test_alerts_endpoint(self, auth_token):
        """Test predictive alerts"""
        response = client.get(
            "/api/predictions/alerts",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "alerts" in data
        assert isinstance(data["alerts"], list)
    
    def test_alerts_data_structure(self, auth_token):
        """Test alerts data structure"""
        response = client.get(
            "/api/predictions/alerts",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        data = response.json()
        
        if len(data["alerts"]) > 0:
            alert = data["alerts"][0]
            assert "district" in alert
            assert "severity" in alert
            assert "message" in alert
            
            # Validate severity values
            assert alert["severity"] in ["low", "medium", "high", "critical"]
    
    def test_alerts_unauthorized(self):
        """Test alerts without authentication"""
        response = client.get("/api/predictions/alerts")
        assert response.status_code == 401
    
    def test_alerts_severity_levels(self, auth_token):
        """Test that alerts have valid severity levels"""
        response = client.get(
            "/api/predictions/alerts",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        data = response.json()
        valid_severities = {"low", "medium", "high", "critical"}
        
        for alert in data["alerts"]:
            assert alert["severity"] in valid_severities
