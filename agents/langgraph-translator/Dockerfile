FROM python:3.10-slim

WORKDIR /app

# Copy shared modules and central config
COPY shared/ /app/shared/
COPY agents_config.yaml /app/

# Install requirements
COPY agents/langgraph-translator/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy agent
COPY agents/langgraph-translator/agent.py .

# Environment variables (can be overridden)
ENV AGENT_NAME=langgraph-translator
ENV CONFIG_PATH=/app/agents_config.yaml
ENV PYTHONUNBUFFERED=1

CMD ["python", "agent.py"]