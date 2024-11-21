# Use NVIDIA CUDA as the base image
FROM nvidia/cuda:12.6.2-cudnn-devel-ubuntu22.04 AS builder

# Set up environment variables for Python installation
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install dependencies and Python
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install requirements
WORKDIR /app
COPY requirements.txt .
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt

# Download SpaCy language model
RUN python3 -m spacy download nl_core_news_md

# Add application files and run the OpenAPI generation script
COPY . .
RUN python3 generate_openapi.py

# Final stage for the application runtime
FROM nvidia/cuda:12.6.2-cudnn-devel-ubuntu22.04

# Set up environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Copy Python environment and app files from the builder stage
COPY --from=builder /usr/local /usr/local
COPY --from=builder /app /app

WORKDIR /app

# Expose the application port
EXPOSE 5000

# Default command
CMD ["gunicorn", "app:app", "--workers", "8", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:5000", "--timeout", "120"]
