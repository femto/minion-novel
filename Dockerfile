# Use Python 3.11 as base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Expose the port for ADK web
EXPOSE 8000

# Set environment variable for port
ENV PORT=8000

# Create a startup script that handles ADK web
RUN echo '#!/bin/bash\n\
if [ -z "$GEMINI_API_KEY" ]; then\n\
    echo "Warning: GEMINI_API_KEY environment variable is not set"\n\
    echo "Please set your Gemini API key in the Hugging Face Space settings"\n\
fi\n\
\n\
# Start the ADK web server\n\
adk web --port $PORT\n\
' > /app/start.sh && chmod +x /app/start.sh

# Start the application
CMD ["/app/start.sh"] 