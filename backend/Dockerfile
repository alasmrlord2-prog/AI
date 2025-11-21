FROM python:3.11-slim

WORKDIR /app

# Install network tools
RUN apt-get update && \
    apt-get install -y iproute2 net-tools procps curl && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app

ENV PYTHONPATH=/app
ENV OLLAMA_URL=http://ollama:11434

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

