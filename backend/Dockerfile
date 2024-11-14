# Stage 1: Build stage
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    libffi-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Stage 2: Final image
FROM python:3.11-slim

WORKDIR /app

RUN useradd -m nonrootuser

# Copy application code and dependencies from builder
COPY --from=builder /app /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

RUN chown -R nonrootuser:nonrootuser /app

ENV PYTHONUNBUFFERED=1
USER nonrootuser

EXPOSE 5000

CMD ["gunicorn", "app:app", "--workers", "8", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:5000", "--timeout", "120"]
