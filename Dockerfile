FROM python:3.11-slim AS base

# Set Build arguments
ARG PYTHON_VERSION=3.11
ARG VERSION=0.0.1
ARG BUILD_DATE

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy only requirements to cache them in docker layer
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app

# Set the entrypoint
ENTRYPOINT ["python", "main.py"]