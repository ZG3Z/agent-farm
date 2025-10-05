"""
Unit tests for Weather Agent
"""
import sys
import time
import requests
import pytest

sys.path.insert(0, 'shared')
from a2a import A2AClient

ENDPOINT = "http://localhost:8081"
AGENT_ID = "crewai-weather"


def wait_for_agent(max_retries=30, retry_delay=2):
    """Wait for agent to be ready"""
    for i in range(max_retries):
        try:
            response = requests.get(f"{ENDPOINT}/health", timeout=5)
            if response.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            if i < max_retries - 1:
                time.sleep(retry_delay)
    return False


class TestWeatherHealth:
    """Health check tests"""
    
    def test_agent_is_running(self):
        """Test: Agent responds to health check"""
        assert wait_for_agent(), "Agent failed to start"
        response = requests.get(f"{ENDPOINT}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["agent"] == AGENT_ID
    
    def test_agent_info_endpoint(self):
        """Test: Agent info endpoint returns correct data"""
        response = requests.get(f"{ENDPOINT}/info")
        assert response.status_code == 200
        data = response.json()
        assert data["agent_id"] == AGENT_ID
        assert data["framework"] == "crewai"
        assert "capabilities" in data


class TestWeatherCapabilities:
    """Capability tests"""
    
    @pytest.fixture
    def client(self):
        """Create A2A client"""
        return A2AClient(agent_id="test_client")
    
    def test_get_weather_valid_location(self, client):
        """Test: Get weather for valid location"""
        result = client.send_request(
            to_agent=AGENT_ID,
            endpoint=ENDPOINT,
            payload={
                "action": "get_weather",
                "location": "London"
            }
        )
        assert result["status"] == "success"
        assert "weather_info" in result
        assert result["location"] == "London"
        assert len(result["weather_info"]) > 0
    
    def test_get_weather_different_city(self, client):
        """Test: Get weather for different city"""
        result = client.send_request(
            to_agent=AGENT_ID,
            endpoint=ENDPOINT,
            payload={
                "action": "get_weather",
                "location": "Tokyo"
            }
        )
        assert result["status"] == "success"
        assert "weather_info" in result
        assert result["location"] == "Tokyo"
    
    def test_get_weather_with_country(self, client):
        """Test: Get weather with country specified"""
        result = client.send_request(
            to_agent=AGENT_ID,
            endpoint=ENDPOINT,
            payload={
                "action": "get_weather",
                "location": "Paris, France"
            }
        )
        assert result["status"] == "success"
        assert "weather_info" in result
    
    def test_get_weather_empty_location(self, client):
        """Test: Error on empty location"""
        result = client.send_request(
            to_agent=AGENT_ID,
            endpoint=ENDPOINT,
            payload={
                "action": "get_weather",
                "location": ""
            }
        )
        assert result["status"] == "error"
        assert "message" in result
    
    def test_unknown_action(self, client):
        """Test: Error on unknown action"""
        result = client.send_request(
            to_agent=AGENT_ID,
            endpoint=ENDPOINT,
            payload={
                "action": "unknown_action",
                "location": "Berlin"
            }
        )
        assert result["status"] == "error"


class TestWeatherMetadata:
    """Metadata tests"""
    
    def test_response_contains_framework_info(self):
        """Test: Response includes framework metadata"""
        client = A2AClient(agent_id="test_client")
        result = client.send_request(
            to_agent=AGENT_ID,
            endpoint=ENDPOINT,
            payload={
                "action": "get_weather",
                "location": "Berlin"
            }
        )
        assert "framework" in result
        assert result["framework"] == "crewai"
        assert "provider" in result
        assert "model" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])