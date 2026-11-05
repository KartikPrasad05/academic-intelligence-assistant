# =============================================================================
# DOCKERFILE FOR CAMPUSINTEL CLOUD RAG
# Optimized for AWS ECS Fargate, AWS App Runner, and GCP Cloud Run
# =============================================================================

FROM python:3.11-slim

# Set working directory and environment variables
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8501

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency requirements
COPY requirements.txt .

# Install python dependencies with minimal footprint
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and college knowledge base
COPY . .

# Healthcheck for AWS ALB / Cloud Run container lifecycle
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Expose standard Streamlit port
EXPOSE 8501

# Run the cloud RAG application
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
