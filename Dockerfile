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

# Health check (using curl instead of requests)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Railway will provide the start command via railway.toml
# No CMD needed here
