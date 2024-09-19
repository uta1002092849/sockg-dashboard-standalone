# Use prebuilt image with Python 3.10
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Update and install git and curl
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt
