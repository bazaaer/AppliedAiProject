# Stage 1: Build stage
FROM python:3.11-slim AS builder

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    libffi-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --user --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Stage 2: Final image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Create a non-root user
RUN useradd -m nonrootuser

# Copy only the necessary files from the builder stage
COPY --from=builder /root/.local /home/nonrootuser/.local
COPY --from=builder /app /app

# Adjust ownership and permissions
RUN chown -R nonrootuser:nonrootuser /app
RUN chown -R nonrootuser:nonrootuser /home/nonrootuser/.local

# Set environment variables
ENV PATH=/home/nonrootuser/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

# Switch to the non-root user
USER nonrootuser

# Expose port 5000
EXPOSE 5000

# Command to run the application using Gunicorn with Uvicorn workers
CMD ["gunicorn", "app:app", "--workers", "8", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:5000", "--timeout", "120"]