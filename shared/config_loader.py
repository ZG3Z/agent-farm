"""
Configuration loader for agents
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def load_agent_config(agent_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Load agent configuration from YAML file or environment variables.
    """
    if agent_name is None:
        agent_name = os.getenv("AGENT_NAME")
        if not agent_name:
            raise ValueError("AGENT_NAME environment variable not set")

    # Try loading from environment variables first
    if _has_env_config():
        logger.info(f"Loading config for {agent_name} from environment variables")
        return _load_from_env()

    # Fallback to YAML file
    config_path = os.getenv("CONFIG_PATH", "/app/agents_config.yaml")

    if not os.path.exists(config_path):
        raise ValueError(
            f"Config file not found: {config_path}. "
            "Set environment variables or provide agents_config.yaml"
        )

    logger.info(f"Loading config for {agent_name} from {config_path}")

    with open(config_path) as f:
        config = yaml.safe_load(f)

    if "agents" not in config or agent_name not in config["agents"]:
        raise ValueError(
            f"Agent {agent_name} not found in {config_path}. "
            "Available agents: {list(config.get('agents', {}).keys())}"
        )

    return config["agents"][agent_name]


def _has_env_config() -> bool:
    """Check if all required environment variables are set"""
    required_vars = [
        "PROVIDER",
        "MODEL",
        "API_KEY_ENV",
        "TEMPERATURE",
        "PORT",
        "ENDPOINT",
    ]
    return all(os.getenv(var) for var in required_vars)


def _load_from_env() -> Dict[str, Any]:
    """Load configuration from environment variables"""
    required_vars = {
        "PROVIDER": "provider",
        "MODEL": "model",
        "API_KEY_ENV": "api_key_env",
        "TEMPERATURE": "temperature",
        "PORT": "port",
        "ENDPOINT": "endpoint",
    }

    missing = [env_var for env_var in required_vars.keys() if not os.getenv(env_var)]

    if missing:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing)}. "
            "Set PROVIDER, MODEL, API_KEY_ENV, TEMPERATURE, PORT, and ENDPOINT"
        )

    config = {
        "provider": os.getenv("PROVIDER"),
        "model": os.getenv("MODEL"),
        "temperature": float(os.getenv("TEMPERATURE")),
        "port": int(os.getenv("PORT")),
        "endpoint": os.getenv("ENDPOINT"),
        "api_key_env": os.getenv("API_KEY_ENV"),
    }

    return config


def get_api_key(api_key_env: str) -> str:
    api_key = os.getenv(api_key_env)
    if not api_key:
        raise ValueError(
            f"API key not found: {api_key_env}. "
            f"Make sure {api_key_env} environment variable is set"
        )
    return api_key
