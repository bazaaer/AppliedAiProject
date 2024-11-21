FROM nvidia/cuda:12.6.2-runtime-ubuntu22.04

# Install system and Python dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set up Python environment
WORKDIR /app

# Copy application files and install Python dependencies
COPY requirements.txt . 
RUN pip3 install --no-cache-dir -r requirements.txt && \
    python3 -m spacy download nl_core_news_md

# Copy application files
COPY . .

# Generate OpenAPI docs
RUN python3 generate_openapi.py

# Expose application port
EXPOSE 5000

# Default command for Gunicorn
CMD ["gunicorn", "app:app", "--workers", "8", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:5000", "--timeout", "120"]
