FROM python:3.10-slim

WORKDIR /app

COPY shared/ /app/shared/
COPY agents_config.yaml /app/

COPY agents/simple-extractor/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY agents/simple-extractor/agent.py .

ENV AGENT_NAME=simple-extractor
ENV CONFIG_PATH=/app/agents_config.yaml
ENV PYTHONUNBUFFERED=1

CMD ["python", "agent.py"]