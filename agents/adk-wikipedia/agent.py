"""
ADK Wikipedia - simple Wikipedia search using Google ADK
Framework: Google ADK
Task: Search Wikipedia and summarize
"""
import os
import sys
import yaml
import logging
import wikipedia

sys.path.insert(0, '/app/shared')

from google.adk.agents import Agent as ADKAgent
from google.adk.tools import FunctionTool
from a2a import A2AServer, A2AMessage, AgentInfo, AgentCapability

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def search_wikipedia(topic: str) -> str:
    """
    Search Wikipedia and return article content.
    
    Args:
        topic: Topic to search
    
    Returns:
        Article content (first 1500 chars)
    """
    try:
        wikipedia.set_lang("en")
        page = wikipedia.page(topic, auto_suggest=True)
        return f"Title: {page.title}\n\nContent: {page.content[:1500]}"
    except wikipedia.exceptions.DisambiguationError as e:
        # Pick first option
        page = wikipedia.page(e.options[0])
        return f"Title: {page.title}\n\nContent: {page.content[:1500]}"
    except wikipedia.exceptions.PageError:
        return f"No article found for: {topic}"


class ADKWikipedia:
    """Simple Wikipedia agent using Google ADK"""
    
    def __init__(self):
        # Load config
        config_path = os.getenv("CONFIG_PATH", "/app/agents_config.yaml")
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        agent_name = os.getenv("AGENT_NAME", "adk-wikipedia")
        agent_config = config["agents"][agent_name]
        
        self.provider = agent_config["provider"]
        self.model_name = agent_config["model"]
        self.temperature = agent_config["temperature"]
        self.port = agent_config["port"]
        self.endpoint = agent_config["endpoint"]
        
        # Create ADK Agent (simple!)
        self.agent = ADKAgent(
            name="wiki_agent",
            model=self.model_name,
            instruction="Search Wikipedia and provide a brief 2-3 sentence summary.",
            tools=[FunctionTool(search_wikipedia)]
        )
        
        logger.info(f"ADK Wikipedia: {self.provider}/{self.model_name}")
    
    def search(self, topic: str) -> dict:
        """Search Wikipedia using ADK"""
        logger.info(f"Searching: {topic}")
        
        try:
            # Simple query to ADK agent
            response = self.agent.generate_content(f"Tell me about: {topic}")
            
            return {
                "topic": topic,
                "summary": response.text,
                "source": "Wikipedia via ADK"
            }
        except Exception as e:
            logger.error(f"Error: {e}")
            return {
                "topic": topic,
                "summary": f"Error: {str(e)}",
                "source": None
            }
    
    def handle_a2a_message(self, message: A2AMessage):
        """Handle A2A messages"""
        payload = message.payload
        action = payload.get("action")
        
        if action == "search":
            topic = payload.get("topic", "")
            if not topic:
                return {"status": "error", "message": "No topic"}
            
            result = self.search(topic)
            return {
                "status": "success",
                **result,
                "framework": "adk",
                "provider": self.provider,
                "model": self.model_name
            }
        
        return {"status": "error", "message": f"Unknown action: {action}"}


def main():
    """Start agent"""
    agent = ADKWikipedia()
    
    agent_info = AgentInfo(
        agent_id="adk-wikipedia",
        name="ADK Wikipedia",
        description=f"Wikipedia search using ADK with {agent.provider}",
        endpoint=agent.endpoint,
        capabilities=[
            AgentCapability(
                name="search",
                description="Search Wikipedia",
                input_schema={"topic": "string"},
                output_schema={"summary": "string", "source": "string"}
            )
        ],
        framework="adk",
        model_provider=agent.provider
    )
    
    server = A2AServer(agent_info, agent.handle_a2a_message, agent.port)
    server.run()


if __name__ == "__main__":
    main()

