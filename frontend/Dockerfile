# Use the official Node.js image from the Docker Hub
FROM node:18-slim as build

# Set the working directory in the container
WORKDIR /app

# Copy the package.json and package-lock.json files to the container
COPY package.json package-lock.json /app/

# Install the dependencies
RUN npm install

# Copy the application code to the container
COPY . .

# Build the application
RUN npm run build

# Use the official Node.js image from the Docker Hub
FROM node:18-slim

# Set the working directory in the container
WORKDIR /app

# Copy the package.json and package-lock.json files to the container
COPY package.json package-lock.json /app/

# Install the dependencies
RUN npm install

# Copy the application code to the container
COPY . .

# Expose the port the app runs on
EXPOSE 5173

# Command to run the application
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"] 