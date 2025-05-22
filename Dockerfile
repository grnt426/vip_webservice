FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create necessary directories
RUN mkdir -p instance dumps

# Make scripts executable
RUN chmod +x scripts/*.py

# Set environment variables
ENV FLASK_APP=vip_guild
ENV FLASK_ENV=development

# Create an entrypoint script
RUN echo '#!/bin/sh\n\
python scripts/load_items.py\n\
flask run --host=0.0.0.0\n\
' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

EXPOSE 5000

ENTRYPOINT ["/app/entrypoint.sh"] 