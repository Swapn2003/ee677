# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install necessary packages and required dependencies for Firefox
RUN apt-get update && \
    apt-get install -y \
    firefox-esr \
    wget \
    bzip2 \
    libgtk-3-0 \
    libdbus-glib-1-2 \
    libxt6 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Download a specific version of GeckoDriver
RUN wget -q "https://github.com/mozilla/geckodriver/releases/download/v0.34.0/geckodriver-v0.34.0-linux64.tar.gz" \
    && tar -xvzf geckodriver-v0.34.0-linux64.tar.gz \
    && chmod +x geckodriver \
    && mv geckodriver /usr/local/bin/ \
    && rm geckodriver-v0.34.0-linux64.tar.gz

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
