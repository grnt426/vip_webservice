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

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the container
COPY backend/requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create static directories first
RUN mkdir -p static/assets

# Copy the application code to the container
COPY backend .

# Copy frontend assets from the frontend build stage
COPY --from=frontend-build /frontend/dist/index.html /app/static/
COPY --from=frontend-build /frontend/dist/assets /app/static/assets/

# Expose the port that FastAPI will run on
EXPOSE 8080

# Start the FastAPI application
CMD ["uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "8080"] 