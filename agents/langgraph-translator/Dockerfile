FROM python:3.10-slim

WORKDIR /app

COPY shared/ /app/shared/
COPY agents_config.yaml /app/

COPY agents/langgraph-translator/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY agents/langgraph-translator/agent.py .

ENV AGENT_NAME=langgraph-translator
ENV CONFIG_PATH=/app/agents_config.yaml
ENV PYTHONUNBUFFERED=1

CMD ["python", "agent.py"]