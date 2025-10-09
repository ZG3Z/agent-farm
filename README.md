# Agent Farm

Multi-framework AI agent infrastructure with Agent-to-Agent (A2A) communication protocol.

## Overview

Agent Farm is a scalable system for deploying and orchestrating multiple AI agents. Each agent:
- Runs independently as a microservice
- Can be built with different frameworks (LangGraph, CrewAI, Google ADK, or none)
- Uses different LLM providers (OpenAI, Anthropic, Google Gemini)
- Communicates via lightweight A2A protocol

## Architecture

```
agents/
├── langgraph-translator/    # LangGraph 
├── crewai-weather/          # CrewAI + OpenWeatherMap
├── adk-wikipedia/           # Google ADK 
└── simple-extractor/        # No framework 

shared/
├── a2a.py                   # A2A protocol implementation
├── config_loader.py         # Configuration management
└── llm_config.py            # LLM client factory

terraform/
├── modules/cloud-run-agent/ # Reusable Cloud Run module
├── main.tf                  # Infrastructure as code
└── ...                      # IAM, secrets, registry

.github/workflows/
└── build-and-push.yml       # CI/CD for Docker images
```
