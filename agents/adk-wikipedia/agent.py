"""
Wikipedia Agent
Framework: Google ADK
Task: Search Wikipedia and summarize

Example:
  Input: "Tell me about Artificial Intelligence."
  Output: {
    "topic": "Artificial Intelligence",
    "summary": "Artificial Intelligence (AI) is the simulation of human intelligence processes by machines, especially computer systems. Key applications include expert systems, natural language processing, and machine learning.",
    "source": "Wikipedia via ADK"
  }
"""
import os
import sys
import yaml
import logging
import wikipedia

sys.path.insert(0, '/app/shared')

from google.genai import Client
from a2a import A2AServer, A2AMessage, AgentInfo, AgentCapability

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def search_wikipedia(topic: str) -> str:
    """Search Wikipedia and return article content"""
    try:
        wikipedia.set_lang("en")
        
        # First try exact search without auto-suggest
        try:
            page = wikipedia.page(topic, auto_suggest=False)
            return f"Title: {page.title}\n\nContent: {page.content[:1500]}"
        except wikipedia.exceptions.PageError:
            # If exact match fails, try with auto-suggest
            page = wikipedia.page(topic, auto_suggest=True)
            return f"Title: {page.title}\n\nContent: {page.content[:1500]}"
            
    except wikipedia.exceptions.DisambiguationError as e:
        # Pick first option from disambiguation
        try:
            page = wikipedia.page(e.options[0], auto_suggest=False)
            return f"Title: {page.title}\n\nContent: {page.content[:1500]}"
        except:
            return f"Disambiguation: Multiple articles found for '{topic}'. Options: {', '.join(e.options[:5])}"
    except wikipedia.exceptions.PageError:
        return f"No article found for: {topic}"
    except Exception as e:
        return f"Error searching Wikipedia: {str(e)}"


class ADKWikipedia:
    """Simple Wikipedia agent using Google ADK"""
    
    def __init__(self):
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
        
        api_key = os.getenv(agent_config["api_key_env"])
        if not api_key:
            raise ValueError(f"API key not found: {agent_config['api_key_env']}")
        
        self.client = Client(api_key=api_key)
        
        logger.info(f"ADK Wikipedia: {self.provider}/{self.model_name}")
    
    def search(self, topic: str) -> dict:
        """Search Wikipedia and summarize"""
        logger.info(f"Searching: {topic}")
        
        try:
            # Get Wikipedia content
            wiki_content = search_wikipedia(topic)
            
            # Check if Wikipedia search failed
            if wiki_content.startswith("No article found") or wiki_content.startswith("Error"):
                return {
                    "topic": topic,
                    "summary": wiki_content,
                    "source": "Wikipedia"
                }
            
            # Summarize
            system_instruction = "You are a helpful assistant that summarizes Wikipedia articles concisely."
            user_prompt = f"""Here is a Wikipedia article: 
                            {wiki_content} 
                            Provide a brief 2-3 sentence summary of the main points."""
                
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[
                    {"role": "user", "parts": [{"text": user_prompt}]}
                ],
                config={
                    "temperature": self.temperature,
                    "max_output_tokens": 300,
                    "system_instruction": system_instruction
                }
            )
            
            summary = response.text.strip()
            
            return {
                "topic": topic,
                "summary": summary,
                "source": "Wikipedia via ADK"
            }
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
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