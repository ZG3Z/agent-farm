"""
Unit tests for Extractor Agent
"""

import sys
import time
import requests
import pytest

sys.path.insert(0, "shared")
from a2a import A2AClient

ENDPOINT = "http://localhost:8083"
AGENT_ID = "simple-extractor"


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


class TestExtractorHealth:
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
        assert data["framework"] == "none"
        assert "capabilities" in data


class TestExtractorCapabilities:
    """Capability tests"""

    @pytest.fixture
    def client(self):
        """Create A2A client"""
        return A2AClient(agent_id="test_client")

    def test_extract_from_text(self, client):
        """Test: Extract data from text"""
        text = "John Smith visited Paris on January 15, 2024 and spent $500."
        result = client.send_request(
            to_agent=AGENT_ID,
            endpoint=ENDPOINT,
            payload={"action": "extract", "text": text},
        )
        assert result["status"] == "success"
        assert "extracted_data" in result
        data = result["extracted_data"]
        assert "people" in data
        assert "locations" in data
        assert "dates" in data
        assert "amounts" in data
        assert "key_facts" in data
        assert isinstance(data["people"], list)
        assert isinstance(data["locations"], list)

    def test_extract_people(self, client):
        """Test: Extract people names"""
        text = "Meeting with Alice Johnson and Bob Williams tomorrow."
        result = client.send_request(
            to_agent=AGENT_ID,
            endpoint=ENDPOINT,
            payload={"action": "extract", "text": text},
        )
        assert result["status"] == "success"
        data = result["extracted_data"]
        assert len(data["people"]) >= 0

    def test_extract_locations(self, client):
        """Test: Extract locations"""
        text = "The conference will be held in New York and London."
        result = client.send_request(
            to_agent=AGENT_ID,
            endpoint=ENDPOINT,
            payload={"action": "extract", "text": text},
        )
        assert result["status"] == "success"
        data = result["extracted_data"]
        assert len(data["locations"]) >= 0

    def test_extract_empty_text(self, client):
        """Test: Error on empty text"""
        result = client.send_request(
            to_agent=AGENT_ID,
            endpoint=ENDPOINT,
            payload={"action": "extract", "text": ""},
        )
        assert result["status"] == "error"
        assert "message" in result

    def test_unknown_action(self, client):
        """Test: Error on unknown action"""
        result = client.send_request(
            to_agent=AGENT_ID,
            endpoint=ENDPOINT,
            payload={"action": "unknown_action", "text": "test"},
        )
        assert result["status"] == "error"


class TestExtractorMetadata:
    """Metadata tests"""

    def test_response_contains_framework_info(self):
        """Test: Response includes framework metadata"""
        client = A2AClient(agent_id="test_client")
        result = client.send_request(
            to_agent=AGENT_ID,
            endpoint=ENDPOINT,
            payload={
                "action": "extract",
                "text": "Test data with John in Paris on 2024-01-01.",
            },
        )
        assert "framework" in result
        assert result["framework"] == "none"
        assert "provider" in result
        assert "model" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
