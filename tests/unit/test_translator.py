"""
Unit tests for Translator Agent
"""

import sys
import time
import requests
import pytest

sys.path.insert(0, "shared")
from a2a import A2AClient

ENDPOINT = "http://localhost:8080"
AGENT_ID = "langgraph-translator"


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


class TestTranslatorHealth:
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
        assert data["framework"] == "langgraph"
        assert "capabilities" in data
        assert len(data["capabilities"]) > 0


class TestTranslatorCapabilities:
    """Capability tests"""

    @pytest.fixture
    def client(self):
        """Create A2A client"""
        return A2AClient(agent_id="test_client")

    def test_translate_to_polish(self, client):
        """Test: Translate English to Polish"""
        result = client.send_request(
            to_agent=AGENT_ID,
            endpoint=ENDPOINT,
            payload={
                "action": "translate",
                "text": "Hello world",
                "target_language": "Polish",
            },
        )
        assert result["status"] == "success"
        assert "translated_text" in result
        assert result["target_language"] == "Polish"
        assert len(result["translated_text"]) > 0
        assert result["translated_text"] != "Hello world"

    def test_translate_to_spanish(self, client):
        """Test: Translate English to Spanish"""
        result = client.send_request(
            to_agent=AGENT_ID,
            endpoint=ENDPOINT,
            payload={
                "action": "translate",
                "text": "Good morning",
                "target_language": "Spanish",
            },
        )
        assert result["status"] == "success"
        assert "translated_text" in result
        assert result["target_language"] == "Spanish"

    def test_translate_empty_text(self, client):
        """Test: Error on empty text"""
        result = client.send_request(
            to_agent=AGENT_ID,
            endpoint=ENDPOINT,
            payload={"action": "translate", "text": "", "target_language": "Polish"},
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
        assert "Unknown action" in result["message"]

    def test_translate_long_text(self, client):
        """Test: Translate longer text"""
        long_text = "The quick brown fox jumps over the lazy dog. " * 10
        result = client.send_request(
            to_agent=AGENT_ID,
            endpoint=ENDPOINT,
            payload={
                "action": "translate",
                "text": long_text,
                "target_language": "French",
            },
        )
        assert result["status"] == "success"
        assert len(result["translated_text"]) > 0


class TestTranslatorMetadata:
    """Metadata tests"""

    def test_response_contains_framework_info(self):
        """Test: Response includes framework metadata"""
        client = A2AClient(agent_id="test_client")
        result = client.send_request(
            to_agent=AGENT_ID,
            endpoint=ENDPOINT,
            payload={
                "action": "translate",
                "text": "test",
                "target_language": "German",
            },
        )
        assert "framework" in result
        assert result["framework"] == "langgraph"
        assert "provider" in result
        assert "model" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
