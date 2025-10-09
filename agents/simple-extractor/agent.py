"""
Data Extractor Agent
Framework: None
Task: Extract structured data from text

Example:
  Input: "John Smith visited Paris on January 15, 2024 and spent $500."
  Output: {
    "people": ["John Smith"],
    "locations": ["Paris"],
    "dates": ["January 15, 2024"],
    "amounts": ["$500"]
    "key_facts": ["John Smith visited Paris on January 15, 2024 and spent $500."]
  }
"""

import os
import sys
import json
import logging

sys.path.insert(0, "/app/shared")

from llm_config import create_client
from a2a import A2AServer, A2AMessage, AgentInfo, AgentCapability
from config_loader import load_agent_config, get_api_key

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataExtractor:
    def __init__(self):
        agent_config = load_agent_config()

        self.provider = agent_config["provider"]
        self.model_name = agent_config["model"]
        self.temperature = agent_config["temperature"]
        self.port = agent_config["port"]
        self.endpoint = agent_config["endpoint"]

        api_key = get_api_key(agent_config["api_key_env"])

        self.client = create_client(self.provider, api_key)

        logger.info(f"Data Extractor: {self.provider}/{self.model_name}")
        logger.info(f"Endpoint: {self.endpoint}")

    def extract(self, text):
        system = """Extract structured information. Return ONLY valid JSON:
                    {
                    "people": ["names"],
                    "locations": ["places"],
                    "dates": ["dates"],
                    "amounts": ["money/numbers"],
                    "key_facts": ["facts"]
                    }"""

        try:
            if self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": f"Extract from:\n\n{text}"},
                    ],
                    temperature=self.temperature,
                    response_format={"type": "json_object"},
                )
                result = json.loads(response.choices[0].message.content)
            elif self.provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model_name,
                    system=system,
                    messages=[{"role": "user", "content": f"Extract from:\n\n{text}"}],
                    temperature=self.temperature,
                    max_tokens=500,
                )
                content = response.content[0].text
                start = content.find("{")
                end = content.rfind("}") + 1
                result = json.loads(content[start:end]) if start != -1 else {}
            elif self.provider == "gemini":
                model = self.client.GenerativeModel(
                    model_name=self.model_name, system_instruction=system
                )
                response = model.generate_content(f"Extract from:\n\n{text}")
                content = response.text
                start = content.find("{")
                end = content.rfind("}") + 1
                result = json.loads(content[start:end]) if start != -1 else {}

            default = {
                "people": [],
                "locations": [],
                "dates": [],
                "amounts": [],
                "key_facts": [],
            }
            default.update(result)
            return default
        except Exception as e:
            logger.error(f"Extraction error: {e}")
            return {
                "people": [],
                "locations": [],
                "dates": [],
                "amounts": [],
                "key_facts": [],
                "error": str(e),
            }

    def handle_a2a_message(self, message):
        payload = message.payload
        if payload.get("action") == "extract":
            text = payload.get("text", "")
            if not text:
                return {"status": "error", "message": "No text"}
            extracted_data = self.extract(text)
            return {
                "status": "success",
                "extracted_data": extracted_data,
                "framework": "none",
                "provider": self.provider,
                "model": self.model_name,
            }
        return {"status": "error", "message": "Unknown action"}


def main():
    agent = DataExtractor()
    agent_info = AgentInfo(
        agent_id="simple-extractor",
        name="Data Extractor",
        description=f"Data extraction using {agent.provider}",
        endpoint=agent.endpoint,
        capabilities=[
            AgentCapability(
                name="extract",
                description="Extract structured data",
                input_schema={"text": "string"},
                output_schema={
                    "people": "array",
                    "locations": "array",
                    "dates": "array",
                    "amounts": "array",
                    "key_facts": "array",
                },
            )
        ],
        framework="none",
        model_provider=agent.provider,
    )
    server = A2AServer(agent_info, agent.handle_a2a_message, agent.port)
    server.run()


if __name__ == "__main__":
    main()
