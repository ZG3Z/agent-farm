"""
A2A Protocol Implementation
"""

from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional, List, Callable
from enum import Enum
import json
from datetime import datetime
import uuid
import logging
import requests
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Types of A2A messages"""

    REQUEST = "request"
    RESPONSE = "response"
    ERROR = "error"


@dataclass
class A2AMessage:
    """Standard A2A message format"""

    message_id: str
    from_agent: str
    to_agent: str
    message_type: MessageType
    payload: Dict[str, Any]
    timestamp: Optional[str] = None
    reply_to: Optional[str] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["message_type"] = self.message_type.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "A2AMessage":
        data = data.copy()
        data["message_type"] = MessageType(data["message_type"])
        return cls(**data)


@dataclass
class AgentCapability:
    """Definition of agent capability"""

    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]


@dataclass
class AgentInfo:
    """Agent information for service discovery"""

    agent_id: str
    name: str
    description: str
    endpoint: str
    capabilities: List[AgentCapability]
    framework: str
    model_provider: str
    status: str = "active"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class A2AServer:
    """FastAPI server implementing A2A protocol"""

    def __init__(
        self,
        agent_info: AgentInfo,
        message_handler: Callable[[A2AMessage], Dict[str, Any]],
        port: int = 8080,
    ):
        self.agent_info = agent_info
        self.message_handler = message_handler
        self.port = port
        self.app = FastAPI(title=agent_info.agent_id)
        self._setup_routes()

    def _setup_routes(self):
        """Configure routes"""

        @self.app.get("/health")
        async def health():
            """Health check endpoint"""
            return {"status": "healthy", "agent": self.agent_info.agent_id}

        @self.app.get("/info")
        async def info():
            """Agent information endpoint"""
            return self.agent_info.to_dict()

        @self.app.post("/message")
        async def receive_message(data: dict):
            """Main endpoint for receiving A2A messages"""
            try:
                message = A2AMessage.from_dict(data)

                logger.info(
                    f"Received message {message.message_id} "
                    f"from {message.from_agent}"
                )

                # Call agent's handler
                result = self.message_handler(message)

                # Return response
                response_message = A2AMessage(
                    message_id=str(uuid.uuid4()),
                    from_agent=self.agent_info.agent_id,
                    to_agent=message.from_agent,
                    message_type=MessageType.RESPONSE,
                    payload=result,
                    reply_to=message.message_id,
                )

                return response_message.to_dict()

            except Exception as e:
                logger.error(f"Error processing message: {e}", exc_info=True)

                error_message = A2AMessage(
                    message_id=str(uuid.uuid4()),
                    from_agent=self.agent_info.agent_id,
                    to_agent=message.from_agent if "message" in locals() else "unknown",
                    message_type=MessageType.ERROR,
                    payload={"error": str(e)},
                    reply_to=message.message_id if "message" in locals() else None,
                )

                raise HTTPException(status_code=500, detail=error_message.to_dict())

    def run(self, host: str = "0.0.0.0"):
        """Start FastAPI server with uvicorn"""
        logger.info(
            f"Starting A2A server for {self.agent_info.agent_id} "
            f"on {host}:{self.port}"
        )
        uvicorn.run(self.app, host=host, port=self.port)


class A2AClient:
    """Client for communicating with other agents via A2A protocol"""

    def __init__(self, agent_id: str, timeout: int = 120):
        self.agent_id = agent_id
        self.timeout = timeout
        self._agent_cache: Dict[str, AgentInfo] = {}

    def send_request(
        self, to_agent: str, endpoint: str, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send request to another agent"""
        message = A2AMessage(
            message_id=str(uuid.uuid4()),
            from_agent=self.agent_id,
            to_agent=to_agent,
            message_type=MessageType.REQUEST,
            payload=payload,
        )

        response = requests.post(
            f"{endpoint}/message", json=message.to_dict(), timeout=self.timeout
        )
        response.raise_for_status()

        response_message = A2AMessage.from_dict(response.json())
        return response_message.payload

    def get_agent_info(self, endpoint: str) -> AgentInfo:
        """Get agent information (service discovery)"""
        if endpoint in self._agent_cache:
            return self._agent_cache[endpoint]

        response = requests.get(f"{endpoint}/info", timeout=self.timeout)
        response.raise_for_status()

        agent_info = AgentInfo(**response.json())
        self._agent_cache[endpoint] = agent_info

        return agent_info
