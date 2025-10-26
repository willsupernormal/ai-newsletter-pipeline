# Lightweight Python image for webhook server only
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (minimal)
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy only necessary files for webhook server
COPY requirements-webhook.txt .
COPY start.sh .
COPY api/ ./api/
COPY config/ ./config/
COPY database/ ./database/
COPY services/ ./services/
COPY scrapers/article_scraper.py ./scrapers/
COPY scrapers/__init__.py ./scrapers/
COPY utils/ ./utils/

# Make start script executable
RUN chmod +x start.sh

# Install Python dependencies (minimal set)
RUN pip install --no-cache-dir -r requirements-webhook.txt

# Expose port
EXPOSE 8000

# Health check - Railway uses PORT env var (usually 8080)
# We'll disable the healthcheck and let Railway handle it
# HEALTHCHECK disabled - Railway has its own health monitoring

# Railway will provide the start command via railway.toml
# No CMD needed here
