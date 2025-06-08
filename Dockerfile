# Use the official Python slim image
FROM python:3.13-slim

# Set a working directory
WORKDIR /app

# Copy requirements first (for caching)
COPY src/requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY src/ .

ENTRYPOINT ["python", "main.py"]