"""
Weather Agent
Framework: CrewAI
Task: Get real weather for a location

Example:
  Input: "Get weather for New York"
  Output: {
    "text": "Current weather in New York: Clear sky. Temperature: 22°C (feels like 21°C). Humidity: 60%. Wind speed: 3 m/s. Pressure: 1012 hPa.",
    "raw_data": {
      "temp": 22,
      "feels_like": 21,
      "description": "clear sky",
      "humidity": 60,
      "wind_speed": 3,
      "pressure": 1012
    }
  }
"""

import os
import sys
import yaml
import logging
import requests

sys.path.insert(0, "/app/shared")

from crewai import Agent, Task, Crew
from crewai.llm import LLM
from a2a import A2AServer, A2AMessage, AgentInfo, AgentCapability

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_real_weather(location: str, api_key: str) -> dict:
    """Get weather from OpenWeatherMap API"""
    try:
        url = "http://api.openweathermap.org/data/2.5/weather"
        params = {"q": location, "appid": api_key, "units": "metric"}

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        description = data["weather"][0]["description"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]
        pressure = data["main"]["pressure"]

        weather_text = (
            f"Current weather in {location}: {description.capitalize()}. "
            f"Temperature: {temp}°C (feels like {feels_like}°C). "
            f"Humidity: {humidity}%. Wind speed: {wind_speed} m/s. "
            f"Pressure: {pressure} hPa."
        )

        return {
            "success": True,
            "data": weather_text,
            "raw_data": {
                "temp": temp,
                "feels_like": feels_like,
                "description": description,
                "humidity": humidity,
                "wind_speed": wind_speed,
                "pressure": pressure,
            },
        }

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return {"success": False, "error": f"Location '{location}' not found"}
        elif e.response.status_code == 401:
            return {"success": False, "error": "Invalid OpenWeatherMap API key"}
        else:
            return {"success": False, "error": f"HTTP error: {e.response.status_code}"}
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"Network error: {str(e)}"}
    except KeyError as e:
        return {"success": False, "error": f"Unexpected API response format: {str(e)}"}


class CrewAIWeather:
    def __init__(self):
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

        llm_api_key = os.getenv(agent_config["api_key_env"])
        if not llm_api_key:
            raise ValueError(f"LLM API key not found: {agent_config['api_key_env']}")

        self.weather_api_key = os.getenv("OPENWEATHER_API_KEY")
        if not self.weather_api_key:
            raise ValueError(
                "OPENWEATHER_API_KEY is required. "
                "Get a free API key at https://openweathermap.org/api"
            )

        self.llm = LLM(
            model=f"{self.provider}/{self.model_name}",
            api_key=llm_api_key,
            temperature=self.temperature,
        )

        logger.info(f"CrewAI Weather: {self.provider}/{self.model_name}")
        logger.info("OpenWeatherMap API: configured")

    def get_weather(self, location):
        """Get weather for location from OpenWeatherMap API"""

        # Get weather data
        weather_result = get_real_weather(location, self.weather_api_key)

        if not weather_result["success"]:
            return {"error": weather_result["error"], "location": location}

        weather_data = weather_result["data"]

        weather_agent = Agent(
            role="Weather Communicator",
            goal="Present weather information in a clear, conversational manner",
            backstory="You are a friendly weather reporter who presents weather data clearly.",
            llm=self.llm,
            verbose=False,
            allow_delegation=False,
        )

        weather_task = Task(
            description=f"""Present this weather data in a friendly, conversational format (2-3 sentences):
                            {weather_data}
                            Keep all the specific numbers and details, but make it sound natural and easy to understand.""",
            expected_output="Friendly weather description with all details",
            agent=weather_agent,
        )

        crew = Crew(agents=[weather_agent], tasks=[weather_task], verbose=False)
        result = crew.kickoff()

        if hasattr(result, "raw"):
            friendly_text = str(result.raw).strip()
        else:
            friendly_text = str(result).strip()

        return {"text": friendly_text, "raw_data": weather_result["raw_data"]}

    def handle_a2a_message(self, message):
        payload = message.payload
        if payload.get("action") == "get_weather":
            location = payload.get("location", "")
            if not location:
                return {"status": "error", "message": "No location provided"}

            try:
                weather_result = self.get_weather(location)

                if "error" in weather_result:
                    return {
                        "status": "error",
                        "message": weather_result["error"],
                        "location": location,
                    }

                return {
                    "status": "success",
                    "weather_info": weather_result["text"],
                    "location": location,
                    "temperature": weather_result["raw_data"]["temp"],
                    "feels_like": weather_result["raw_data"]["feels_like"],
                    "description": weather_result["raw_data"]["description"],
                    "humidity": weather_result["raw_data"]["humidity"],
                    "wind_speed": weather_result["raw_data"]["wind_speed"],
                    "framework": "crewai",
                    "provider": self.provider,
                    "model": self.model_name,
                    "data_source": "openweathermap",
                }
            except Exception as e:
                logger.error(f"Weather error: {e}", exc_info=True)
                return {
                    "status": "error",
                    "message": f"Failed to get weather: {str(e)}",
                }

        return {"status": "error", "message": "Unknown action"}


def main():
    agent = CrewAIWeather()
    agent_info = AgentInfo(
        agent_id="crewai-weather",
        name="CrewAI Weather",
        description=f"Real-time weather using OpenWeatherMap API with {agent.provider}",
        endpoint=agent.endpoint,
        capabilities=[
            AgentCapability(
                name="get_weather",
                description="Get current weather for a location",
                input_schema={"location": "string"},
                output_schema={
                    "weather_info": "string",
                    "temperature": "number",
                    "humidity": "number",
                    "data_source": "string",
                },
            )
        ],
        framework="crewai",
        model_provider=agent.provider,
    )
    server = A2AServer(agent_info, agent.handle_a2a_message, agent.port)
    server.run()


if __name__ == "__main__":
    main()
