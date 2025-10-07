"""
Translator Agent
Framework: LangGraph
Task: Translate text to target language

Example:
    Input: "Bonjour tout le monde", target_language="English"
    Output: "Hello everyone"
"""

import os
import sys
import yaml
import logging
from typing import Dict, Any, TypedDict

sys.path.insert(0, "/app/shared")

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from a2a import A2AServer, A2AMessage, AgentInfo, AgentCapability

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TranslationState(TypedDict):
    text: str
    target_language: str
    translated_text: str


def load_agent_config():
    agent_name = os.getenv("AGENT_NAME", "langgraph-translator")

    if os.path.exists("/app/agents_config.yaml"):
        with open("/app/agents_config.yaml") as f:
            config = yaml.safe_load(f)
            return config["agents"][agent_name]

    return {
        "provider": os.getenv("PROVIDER"),
        "model": os.getenv("MODEL"),
        "temperature": float(os.getenv("TEMPERATURE")),
        "port": int(os.getenv("PORT", "8080")),
        "endpoint": os.getenv("ENDPOINT"),
        "api_key_env": os.getenv("API_KEY_ENV"),
    }


class LangGraphTranslator:
    def __init__(self):
        agent_config = load_agent_config()

        self.provider = agent_config["provider"]
        self.model_name = agent_config["model"]
        self.temperature = agent_config["temperature"]
        self.port = agent_config["port"]
        self.endpoint = agent_config["endpoint"]

        api_key = os.getenv(agent_config["api_key_env"])

        self.llm = self._create_llm(api_key)
        self.graph = self._build_graph()

        logger.info(f"LangGraph Translator: {self.provider}/{self.model_name}")

    def _create_llm(self, api_key):
        if self.provider == "openai":
            return ChatOpenAI(
                model=self.model_name, api_key=api_key, temperature=self.temperature
            )
        elif self.provider == "anthropic":
            return ChatAnthropic(
                model=self.model_name, api_key=api_key, temperature=self.temperature
            )
        elif self.provider == "gemini":
            return ChatGoogleGenerativeAI(
                model=self.model_name,
                google_api_key=api_key,
                temperature=self.temperature,
            )

    def _build_graph(self):
        workflow = StateGraph(TranslationState)
        workflow.add_node("translate", self._translate_node)
        workflow.set_entry_point("translate")
        workflow.add_edge("translate", END)
        return workflow.compile()

    def _translate_node(self, state):
        prompt = f"Translate to {state['target_language']}. Return ONLY translation:\n\n{state['text']}"
        response = self.llm.invoke(prompt)
        state["translated_text"] = response.content.strip()
        return state

    def translate(self, text, target_language):
        result = self.graph.invoke(
            TranslationState(
                text=text, target_language=target_language, translated_text=""
            )
        )
        return result["translated_text"]

    def handle_a2a_message(self, message):
        payload = message.payload
        action = payload.get("action")

        if action == "translate":
            text = payload.get("text", "")
            target_language = payload.get("target_language", "English")
            if not text:
                return {"status": "error", "message": "No text"}

            translated = self.translate(text, target_language)
            return {
                "status": "success",
                "translated_text": translated,
                "target_language": target_language,
                "framework": "langgraph",
                "provider": self.provider,
                "model": self.model_name,
            }
        return {"status": "error", "message": f"Unknown action: {action}"}


def main():
    agent = LangGraphTranslator()
    agent_info = AgentInfo(
        agent_id="langgraph-translator",
        name="LangGraph Translator",
        description=f"Translation using {agent.provider}",
        endpoint=agent.endpoint,
        capabilities=[
            AgentCapability(
                name="translate",
                description="Translate text",
                input_schema={"text": "string", "target_language": "string"},
                output_schema={"translated_text": "string"},
            )
        ],
        framework="langgraph",
        model_provider=agent.provider,
    )
    server = A2AServer(agent_info, agent.handle_a2a_message, agent.port)
    server.run()


if __name__ == "__main__":
    main()
