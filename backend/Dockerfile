# Frontend build stage
FROM node:18-slim as frontend-build

# Set the working directory in the container
WORKDIR /frontend

# Copy the frontend package files
COPY frontend/package.json frontend/package-lock.json ./

# Install the dependencies
RUN npm install

# Copy the frontend application code
COPY frontend .

# Build the frontend application
RUN npm run build

# Backend stage
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file from backend directory
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories with proper permissions
RUN mkdir -p /app/data /app/static/assets /app/dumps && \
    chown -R nobody:nogroup /app/data /app/static /app/dumps && \
    chmod -R 755 /app/dumps

# Copy all backend files (including .secrets)
COPY backend/ .

# Copy frontend assets from the frontend build stage
COPY --from=frontend-build /frontend/dist/index.html /app/static/
COPY --from=frontend-build /frontend/dist/assets /app/static/assets/

# Switch to non-root user
USER nobody

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose the port that FastAPI will run on
EXPOSE 8080

# Run the application with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"] 