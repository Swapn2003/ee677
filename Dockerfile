# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Install necessary packages
RUN apt-get update && \
    apt-get install -y \
    firefox-esr \
    wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Download and install Geckodriver
RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.32.0/geckodriver-v0.32.0-linux64.tar.gz && \
    tar -xvzf geckodriver-v0.32.0-linux64.tar.gz && \
    chmod +x geckodriver && \
    mv geckodriver /usr/local/bin/ && \
    rm geckodriver-v0.32.0-linux64.tar.gz

# Copy the current directory contents into the container at /app
COPY . .

# Install required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the app runs on
EXPOSE 5000

# Define environment variable
ENV NAME World

# Run the application
CMD ["python", "app.py"]
