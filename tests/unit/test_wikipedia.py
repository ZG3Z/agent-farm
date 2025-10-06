"""
Unit tests for Wikipedia Agent
"""

import sys
import time
import requests
import pytest

sys.path.insert(0, "shared")
from a2a import A2AClient

ENDPOINT = "http://localhost:8082"
AGENT_ID = "adk-wikipedia"


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


class TestWikipediaHealth:
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
        assert data["framework"] == "adk"
        assert "capabilities" in data


class TestWikipediaCapabilities:
    """Capability tests"""

    @pytest.fixture
    def client(self):
        """Create A2A client"""
        return A2AClient(agent_id="test_client")

    def test_search_valid_topic(self, client):
        """Test: Search for valid Wikipedia topic"""
        result = client.send_request(
            to_agent=AGENT_ID,
            endpoint=ENDPOINT,
            payload={"action": "search", "topic": "Python programming language"},
        )
        assert result["status"] == "success"
        assert "summary" in result
        assert result["topic"] == "Python programming language"
        assert len(result["summary"]) > 0

    def test_search_different_topic(self, client):
        """Test: Search for different topic"""
        result = client.send_request(
            to_agent=AGENT_ID,
            endpoint=ENDPOINT,
            payload={"action": "search", "topic": "Machine Learning"},
        )
        assert result["status"] == "success"
        assert "summary" in result
        assert "source" in result

    def test_search_person(self, client):
        """Test: Search for person"""
        result = client.send_request(
            to_agent=AGENT_ID,
            endpoint=ENDPOINT,
            payload={"action": "search", "topic": "Albert Einstein"},
        )
        assert result["status"] == "success"
        assert "summary" in result

    def test_search_empty_topic(self, client):
        """Test: Error on empty topic"""
        result = client.send_request(
            to_agent=AGENT_ID,
            endpoint=ENDPOINT,
            payload={"action": "search", "topic": ""},
        )
        assert result["status"] == "error"
        assert "message" in result

    def test_unknown_action(self, client):
        """Test: Error on unknown action"""
        result = client.send_request(
            to_agent=AGENT_ID,
            endpoint=ENDPOINT,
            payload={"action": "unknown_action", "topic": "test"},
        )
        assert result["status"] == "error"


class TestWikipediaMetadata:
    """Metadata tests"""

    def test_response_contains_framework_info(self):
        """Test: Response includes framework metadata"""
        client = A2AClient(agent_id="test_client")
        result = client.send_request(
            to_agent=AGENT_ID,
            endpoint=ENDPOINT,
            payload={"action": "search", "topic": "Artificial Intelligence"},
        )
        assert "framework" in result
        assert result["framework"] == "adk"
        assert "provider" in result
        assert "model" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
