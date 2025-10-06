"""
Integration tests for A2A communication between agents
"""

import sys
import time
import requests
import pytest

sys.path.insert(0, "shared")
from a2a import A2AClient

ENDPOINTS = {
    "translator": "http://localhost:8080",
    "weather": "http://localhost:8081",
    "wikipedia": "http://localhost:8082",
    "extractor": "http://localhost:8083",
}


def wait_for_all_agents(max_retries=30, retry_delay=2):
    """Wait for all agents to be ready"""
    for name, endpoint in ENDPOINTS.items():
        for i in range(max_retries):
            try:
                response = requests.get(f"{endpoint}/health", timeout=5)
                if response.status_code == 200:
                    break
            except requests.exceptions.RequestException:
                if i == max_retries - 1:
                    return False
                time.sleep(retry_delay)
    return True


class TestAgentDiscovery:
    """Agent discovery tests"""

    @pytest.fixture(scope="class", autouse=True)
    def wait_agents(self):
        """Wait for all agents before running tests"""
        assert wait_for_all_agents(), "Not all agents started"

    def test_all_agents_running(self):
        """Test: All agents respond to health checks"""
        for name, endpoint in ENDPOINTS.items():
            response = requests.get(f"{endpoint}/health")
            assert response.status_code == 200, f"Agent {name} not healthy"

    def test_all_agents_discoverable(self):
        """Test: All agents provide info endpoint"""
        for name, endpoint in ENDPOINTS.items():
            response = requests.get(f"{endpoint}/info")
            assert response.status_code == 200, f"Agent {name} info not available"
            data = response.json()
            assert "agent_id" in data
            assert "capabilities" in data


class TestWikipediaToTranslator:
    """Pipeline: Wikipedia -> Translator"""

    @pytest.fixture
    def client(self):
        """Create A2A client"""
        return A2AClient(agent_id="integration_test", timeout=60)

    def test_wikipedia_then_translate(self, client):
        """Test: Search Wikipedia then translate result"""
        wiki_result = client.send_request(
            to_agent="adk-wikipedia",
            endpoint=ENDPOINTS["wikipedia"],
            payload={"action": "search", "topic": "Python programming"},
        )
        assert wiki_result["status"] == "success"
        summary = wiki_result["summary"]

        time.sleep(2)

        trans_result = client.send_request(
            to_agent="langgraph-translator",
            endpoint=ENDPOINTS["translator"],
            payload={
                "action": "translate",
                "text": summary[:500],
                "target_language": "Polish",
            },
        )
        assert trans_result["status"] == "success"
        assert len(trans_result["translated_text"]) > 0


class TestExtractorToWikipedia:
    """Pipeline: Extractor -> Wikipedia"""

    @pytest.fixture
    def client(self):
        """Create A2A client"""
        return A2AClient(agent_id="integration_test", timeout=60)

    def test_extract_then_wikipedia(self, client):
        """Test: Extract entities then search Wikipedia"""
        text = "Albert Einstein developed the theory of relativity in Germany."

        extract_result = client.send_request(
            to_agent="simple-extractor",
            endpoint=ENDPOINTS["extractor"],
            payload={"action": "extract", "text": text},
        )
        assert extract_result["status"] == "success"
        data = extract_result["extracted_data"]

        if len(data["people"]) > 0:
            person = data["people"][0]
            time.sleep(2)

            wiki_result = client.send_request(
                to_agent="adk-wikipedia",
                endpoint=ENDPOINTS["wikipedia"],
                payload={"action": "search", "topic": person},
            )
            assert wiki_result["status"] == "success"


class TestWeatherToTranslator:
    """Pipeline: Weather -> Translator"""

    @pytest.fixture
    def client(self):
        """Create A2A client"""
        return A2AClient(agent_id="integration_test", timeout=60)

    def test_weather_then_translate(self, client):
        """Test: Get weather then translate to another language"""
        weather_result = client.send_request(
            to_agent="crewai-weather",
            endpoint=ENDPOINTS["weather"],
            payload={"action": "get_weather", "location": "Tokyo"},
        )
        assert weather_result["status"] == "success"
        weather_info = weather_result["weather_info"]

        time.sleep(2)

        trans_result = client.send_request(
            to_agent="langgraph-translator",
            endpoint=ENDPOINTS["translator"],
            payload={
                "action": "translate",
                "text": weather_info,
                "target_language": "Spanish",
            },
        )
        assert trans_result["status"] == "success"


class TestComplexPipeline:
    """Complex multi-agent pipelines"""

    @pytest.fixture
    def client(self):
        """Create A2A client"""
        return A2AClient(agent_id="integration_test", timeout=60)

    def test_wikipedia_extract_translate(self, client):
        """Test: Wikipedia -> Extractor -> Translator"""
        wiki_result = client.send_request(
            to_agent="adk-wikipedia",
            endpoint=ENDPOINTS["wikipedia"],
            payload={"action": "search", "topic": "Artificial Intelligence"},
        )
        assert wiki_result["status"] == "success"
        summary = wiki_result["summary"]

        time.sleep(2)

        extract_result = client.send_request(
            to_agent="simple-extractor",
            endpoint=ENDPOINTS["extractor"],
            payload={"action": "extract", "text": summary},
        )
        assert extract_result["status"] == "success"

        key_facts = extract_result["extracted_data"].get("key_facts", [])
        if len(key_facts) > 0:
            time.sleep(2)

            trans_result = client.send_request(
                to_agent="langgraph-translator",
                endpoint=ENDPOINTS["translator"],
                payload={
                    "action": "translate",
                    "text": " ".join(key_facts[:3]),
                    "target_language": "German",
                },
            )
            assert trans_result["status"] == "success"

    def test_extract_wikipedia_weather(self, client):
        """Test: Extract location -> Wikipedia -> Weather"""
        text = "Planning a trip to Paris next month."

        extract_result = client.send_request(
            to_agent="simple-extractor",
            endpoint=ENDPOINTS["extractor"],
            payload={"action": "extract", "text": text},
        )
        assert extract_result["status"] == "success"

        locations = extract_result["extracted_data"].get("locations", [])
        if len(locations) > 0:
            location = locations[0]
            time.sleep(2)

            wiki_result = client.send_request(
                to_agent="adk-wikipedia",
                endpoint=ENDPOINTS["wikipedia"],
                payload={"action": "search", "topic": location},
            )
            assert wiki_result["status"] == "success"

            time.sleep(2)

            weather_result = client.send_request(
                to_agent="crewai-weather",
                endpoint=ENDPOINTS["weather"],
                payload={"action": "get_weather", "location": location},
            )
            assert weather_result["status"] == "success"

    def test_full_pipeline_all_agents(self, client):
        """Test: Use all 4 agents in sequence"""
        topic_text = "Steve Jobs founded Apple in California."

        extract_result = client.send_request(
            to_agent="simple-extractor",
            endpoint=ENDPOINTS["extractor"],
            payload={"action": "extract", "text": topic_text},
        )
        assert extract_result["status"] == "success"

        people = extract_result["extracted_data"].get("people", [])
        if len(people) > 0:
            person = people[0]
            time.sleep(2)

            wiki_result = client.send_request(
                to_agent="adk-wikipedia",
                endpoint=ENDPOINTS["wikipedia"],
                payload={"action": "search", "topic": person},
            )
            assert wiki_result["status"] == "success"

            time.sleep(2)

            trans_result = client.send_request(
                to_agent="langgraph-translator",
                endpoint=ENDPOINTS["translator"],
                payload={
                    "action": "translate",
                    "text": wiki_result["summary"][:300],
                    "target_language": "French",
                },
            )
            assert trans_result["status"] == "success"

        locations = extract_result["extracted_data"].get("locations", [])
        if len(locations) > 0:
            location = locations[0]
            time.sleep(2)

            weather_result = client.send_request(
                to_agent="crewai-weather",
                endpoint=ENDPOINTS["weather"],
                payload={"action": "get_weather", "location": location},
            )
            assert weather_result["status"] == "success"


class TestConcurrentRequests:
    """Concurrent communication tests"""

    @pytest.fixture
    def client(self):
        """Create A2A client"""
        return A2AClient(agent_id="integration_test", timeout=60)

    def test_multiple_translations_sequential(self, client):
        """Test: Multiple translation requests with delays"""
        texts = ["Hello", "Goodbye", "Thank you"]
        languages = ["French", "Spanish", "German"]
        results = []

        for text, lang in zip(texts, languages):
            if len(results) > 0:
                time.sleep(2)

            result = client.send_request(
                to_agent="langgraph-translator",
                endpoint=ENDPOINTS["translator"],
                payload={"action": "translate", "text": text, "target_language": lang},
            )
            results.append(result)
            assert result["status"] == "success"

        assert len(results) == 3

    def test_different_agents_sequential(self, client):
        """Test: Sequential requests to different agents"""
        trans_result = client.send_request(
            to_agent="langgraph-translator",
            endpoint=ENDPOINTS["translator"],
            payload={
                "action": "translate",
                "text": "Test",
                "target_language": "Spanish",
            },
        )
        assert trans_result["status"] == "success"

        time.sleep(2)

        weather_result = client.send_request(
            to_agent="crewai-weather",
            endpoint=ENDPOINTS["weather"],
            payload={"action": "get_weather", "location": "Madrid"},
        )
        assert weather_result["status"] == "success"

        time.sleep(2)

        wiki_result = client.send_request(
            to_agent="adk-wikipedia",
            endpoint=ENDPOINTS["wikipedia"],
            payload={"action": "search", "topic": "Spain"},
        )
        assert wiki_result["status"] == "success"


class TestErrorHandling:
    """Error handling in A2A communication"""

    @pytest.fixture
    def client(self):
        """Create A2A client"""
        return A2AClient(agent_id="integration_test", timeout=60)

    def test_invalid_action_returns_error(self, client):
        """Test: Invalid action returns proper error"""
        result = client.send_request(
            to_agent="langgraph-translator",
            endpoint=ENDPOINTS["translator"],
            payload={"action": "invalid_action", "text": "test"},
        )
        assert result["status"] == "error"

    def test_missing_required_field(self, client):
        """Test: Missing required field returns error"""
        time.sleep(2)

        result = client.send_request(
            to_agent="langgraph-translator",
            endpoint=ENDPOINTS["translator"],
            payload={"action": "translate", "target_language": "Spanish"},
        )
        assert result["status"] == "error"

    def test_empty_payload(self, client):
        """Test: Empty payload returns error"""
        time.sleep(2)

        result = client.send_request(
            to_agent="simple-extractor",
            endpoint=ENDPOINTS["extractor"],
            payload={"action": "extract", "text": ""},
        )
        assert result["status"] == "error"


class TestCrossFrameworkCompatibility:
    """Test compatibility between different frameworks"""

    @pytest.fixture
    def client(self):
        """Create A2A client"""
        return A2AClient(agent_id="integration_test", timeout=60)

    def test_langgraph_to_crewai(self, client):
        """Test: LangGraph output to CrewAI input"""
        trans_result = client.send_request(
            to_agent="langgraph-translator",
            endpoint=ENDPOINTS["translator"],
            payload={
                "action": "translate",
                "text": "What is the weather?",
                "target_language": "French",
            },
        )
        assert trans_result["status"] == "success"

    def test_crewai_to_adk(self, client):
        """Test: CrewAI output to ADK input"""
        time.sleep(2)

        weather_result = client.send_request(
            to_agent="crewai-weather",
            endpoint=ENDPOINTS["weather"],
            payload={"action": "get_weather", "location": "Paris"},
        )
        assert weather_result["status"] == "success"

    def test_adk_to_none(self, client):
        """Test: ADK output to no-framework agent input"""
        time.sleep(2)

        wiki_result = client.send_request(
            to_agent="adk-wikipedia",
            endpoint=ENDPOINTS["wikipedia"],
            payload={"action": "search", "topic": "Machine Learning"},
        )
        assert wiki_result["status"] == "success"

        time.sleep(2)

        extract_result = client.send_request(
            to_agent="simple-extractor",
            endpoint=ENDPOINTS["extractor"],
            payload={"action": "extract", "text": wiki_result["summary"]},
        )
        assert extract_result["status"] == "success"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
