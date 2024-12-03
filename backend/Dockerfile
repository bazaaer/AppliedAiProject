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

# Default command
CMD ["uvicorn", "--host", "0.0.0.0", "--port", "5000", "--loop", "uvloop", "--http", "h11", "--interface", "asgi3", "--no-access-log", "--workers", "8", "app:app"]
