import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


@pytest.fixture
def auth_token():
    """Fixture to get authentication token"""
    response = client.post("/api/auth/login", json={
        "email": "admin@ksp.gov.in",
        "password": "Admin@123"
    })
    return response.json()["access_token"]


class TestNetworkAnalysis:
    """Test suite for network analysis endpoints"""
    
    def test_network_graph_endpoint(self, auth_token):
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
    
    def test_network_graph_with_criminal_name(self, auth_token):
        """Test network graph with criminal name filter"""
        response = client.post(
            "/api/network/graph",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"criminal_name": "Test Criminal"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "nodes" in data
        assert "links" in data
    
    def test_network_graph_structure(self, auth_token):
        """Test network graph data structure"""
        response = client.post(
            "/api/network/graph",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"crime_id": 1}
        )
        
        data = response.json()
        
        # Check node structure
        if len(data["nodes"]) > 0:
            node = data["nodes"][0]
            assert "id" in node
            assert "name" in node
            assert "crimeCount" in node
            assert isinstance(node["crimeCount"], int)
            assert node["crimeCount"] >= 0
        
        # Check link structure
        if len(data["links"]) > 0:
            link = data["links"][0]
            assert "source" in link
            assert "target" in link
            assert isinstance(link["source"], str)
            assert isinstance(link["target"], str)
    
    def test_network_graph_unauthorized(self):
        """Test network graph without authentication"""
        response = client.post(
            "/api/network/graph",
            json={"crime_id": 123}
        )
        assert response.status_code == 401
    
    def test_network_graph_empty_request(self, auth_token):
        """Test network graph with empty request"""
        response = client.post(
            "/api/network/graph",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={}
        )
        assert response.status_code == 200
        # Should still return valid structure even with no filters
        data = response.json()
        assert "nodes" in data
        assert "links" in data
    
    def test_network_graph_relationships(self, auth_token):
        """Test that links connect valid nodes"""
        response = client.post(
            "/api/network/graph",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"crime_id": 1}
        )
        
        data = response.json()
        node_ids = {node["id"] for node in data["nodes"]}
        
        # All link sources and targets should be valid node IDs
        for link in data["links"]:
            assert link["source"] in node_ids, f"Source {link['source']} not in nodes"
            assert link["target"] in node_ids, f"Target {link['target']} not in nodes"
    
    def test_network_graph_node_uniqueness(self, auth_token):
        """Test that node IDs are unique"""
        response = client.post(
            "/api/network/graph",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"crime_id": 1}
        )
        
        data = response.json()
        node_ids = [node["id"] for node in data["nodes"]]
        
        # All node IDs should be unique
        assert len(node_ids) == len(set(node_ids)), "Duplicate node IDs found"
