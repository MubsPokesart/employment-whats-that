# Use official Playwright Python image (Ubuntu-based)
FROM mcr.microsoft.com/playwright/python:v1.48.0-jammy

# Install build dependencies for AWS Lambda Runtime Interface Client
RUN apt-get update && apt-get install -y \
    g++ \
    make \
    cmake \
    unzip \
    libcurl4-openssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install AWS Lambda Runtime Interface Client
RUN pip install awslambdaric

# Copy application code
COPY src/ ./src/

# Set Lambda handler
ENV HANDLER_MODULE=src.handler
ENV HANDLER_FUNCTION=lambda_handler

# Entry point for Lambda
ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]
CMD [ "src.handler.lambda_handler" ]
