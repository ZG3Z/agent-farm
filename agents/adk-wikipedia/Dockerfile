FROM python:3.10-slim

WORKDIR /app

COPY shared/ /app/shared/
COPY agents_config.yaml /app/

COPY agents/adk-wikipedia/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY agents/adk-wikipedia/agent.py .

ENV AGENT_NAME=adk-wikipedia
ENV CONFIG_PATH=/app/agents_config.yaml
ENV PYTHONUNBUFFERED=1

CMD ["python", "agent.py"]