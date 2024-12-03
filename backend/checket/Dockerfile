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
    python3 -m spacy download nl_core_news_md

# Copy application files
COPY . .

# Ensure the correct Python binary is used
ENV PATH="/usr/local/bin:$PATH"

# Deploy the ray serve application
RUN ["ray", "start", "--head"]
CMD ["ray", "deploy" "config.yaml"]