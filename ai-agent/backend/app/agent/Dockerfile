FROM python:3.11-slim

WORKDIR /app

# Copy packages
COPY agent /app/agent
COPY tools /app/tools
COPY memory /app/memory
COPY logs /app/logs
COPY main.py /app/main.py

RUN pip install requests

CMD ["python3", "-u", "-m", "agent.agent"]

