# Builder Stage
FROM nvidia/cuda:12.6.2-runtime-ubuntu22.04 AS builder

# Install Python and pip
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install requirements and SpaCy model
WORKDIR /app
COPY requirements.txt .
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt && \
    python3 -m spacy download nl_core_news_md

# Copy application files
COPY . .
RUN python3 generate_openapi.py

# Runtime Stage
FROM nvidia/cuda:12.6.2-runtime-ubuntu22.04

# Copy only the necessary files from builder
COPY --from=builder /usr/local /usr/local
COPY --from=builder /app /app

WORKDIR /app

# Expose the application port
EXPOSE 5000

# Default command for Gunicorn
CMD ["gunicorn", "app:app", "--workers", "8", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:5000", "--timeout", "120"]
