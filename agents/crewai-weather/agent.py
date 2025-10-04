"""
Weather Agent implemented with CrewAI
"""
import os
import sys
import yaml
import logging

sys.path.insert(0, '/app/shared')

from crewai import Agent, Task, Crew
from crewai.llm import LLM
from a2a import A2AServer, A2AMessage, AgentInfo, AgentCapability

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CrewAIWeather:
    def __init__(self):
        # Load YAML config
        config_path = os.getenv("CONFIG_PATH", "/app/agents_config.yaml")
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        agent_name = os.getenv("AGENT_NAME", "crewai-weather")
        agent_config = config["agents"][agent_name]
        
        self.provider = agent_config["provider"]
        self.model_name = agent_config["model"]
        self.temperature = agent_config["temperature"]
        self.port = agent_config["port"]
        self.endpoint = agent_config["endpoint"]
        
        api_key = os.getenv(agent_config["api_key_env"])
        if not api_key:
            raise ValueError(f"API key not found: {agent_config['api_key_env']}")
        
        self.llm = LLM(
            model=f"{self.provider}/{self.model_name}",
            api_key=api_key,
            temperature=self.temperature
        )
        
        logger.info(f"CrewAI Weather: {self.provider}/{self.model_name}")
    
    def get_weather(self, location):
        weather_agent = Agent(
            role="Weather Analyst",
            goal=f"Provide weather for {location}",
            backstory="Meteorologist",
            llm=self.llm,
            verbose=False,
            allow_delegation=False
        )
        weather_task = Task(
            description=f"Weather for {location}. Brief (2-3 sentences).",
            expected_output="Brief weather report",
            agent=weather_agent
        )
        crew = Crew(agents=[weather_agent], tasks=[weather_task], verbose=False)
        return str(crew.kickoff()).strip()
    
    def handle_a2a_message(self, message):
        payload = message.payload
        if payload.get("action") == "get_weather":
            location = payload.get("location", "")
            if not location:
                return {"status": "error", "message": "No location"}
            weather_info = self.get_weather(location)
            return {
                "status": "success",
                "weather_info": weather_info,
                "location": location,
                "framework": "crewai",
                "provider": self.provider,
                "model": self.model_name
            }
        return {"status": "error", "message": "Unknown action"}


def main():
    agent = CrewAIWeather()
    agent_info = AgentInfo(
        agent_id="crewai-weather",
        name="CrewAI Weather",
        description=f"Weather using {agent.provider}",
        endpoint=agent.endpoint,
        capabilities=[
            AgentCapability(
                name="get_weather",
                description="Get weather",
                input_schema={"location": "string"},
                output_schema={"weather_info": "string"}
            )
        ],
        framework="crewai",
        model_provider=agent.provider
    )
    server = A2AServer(agent_info, agent.handle_a2a_message, agent.port)
    server.run()

if __name__ == "__main__":
    main()

