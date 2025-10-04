FROM python:3.10-slim

WORKDIR /app

COPY shared/ /app/shared/
COPY agents_config.yaml /app/

COPY agents/crewai-weather/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY agents/crewai-weather/agent.py .

ENV AGENT_NAME=crewai-weather
ENV CONFIG_PATH=/app/agents_config.yaml
ENV PYTHONUNBUFFERED=1

CMD ["python", "agent.py"]