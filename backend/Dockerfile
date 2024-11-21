# Single-stage: Build and Runtime with CUDA
FROM nvidia/cuda:12.6.2-devel-ubuntu22.04

# Install required dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt . 
RUN pip3 install --no-cache-dir -r requirements.txt && \
    python3 -m spacy download nl_core_news_md && \
    which gunicorn && gunicorn --version

# Copy application files
COPY . .

# Generate OpenAPI specification
RUN python3 generate_openapi.py

# Expose application port
EXPOSE 5000

# Ensure the correct Python binary is used
ENV PATH="/usr/local/bin:$PATH"

# Default command
CMD ["gunicorn", "app:app", "--workers", "8", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:5000", "--timeout", "120"]
