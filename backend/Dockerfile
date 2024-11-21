# Stage 1: Build stage
FROM nvidia/cuda:12.6.2-cudnn-devel-ubuntu22.04 AS builder

WORKDIR /app

# Install dependencies for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    libffi-dev \
    gcc \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Copy application requirements and install dependencies
COPY requirements.txt ./ 
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Stage 2: Final image
FROM nvidia/cuda:12.6.2-cudnn-devel-ubuntu22.04

WORKDIR /app

# Add a non-root user
RUN useradd -m nonrootuser

# Copy application code and dependencies from builder
COPY --from=builder /app /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

RUN chown -R nonrootuser:nonrootuser /app

# Set Python environment variables
ENV PYTHONUNBUFFERED=1

# Switch to non-root user
USER nonrootuser

# Expose application port
EXPOSE 5000

# Run generate_openapi.py to prepare the app
RUN python3 generate_openapi.py

# Default command
CMD ["gunicorn", "app:app", "--workers", "8", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:5000", "--timeout", "120"]
