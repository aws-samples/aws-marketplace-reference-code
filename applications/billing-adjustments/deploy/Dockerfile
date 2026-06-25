# Container image for the Billing Adjustments web app, intended to run inside an
# AWS account (e.g. AWS App Runner) using an attached IAM role for credentials.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    MANAGED_CREDENTIALS=true \
    PORT=8080

WORKDIR /app

# Install dependencies first for better layer caching
COPY deploy/requirements-deploy.txt /app/requirements-deploy.txt
RUN pip install --no-cache-dir -r /app/requirements-deploy.txt

# Copy the shared engine package and the web application
COPY core/ /app/core/
COPY webapp/ /app/webapp/

WORKDIR /app/webapp

# Writable location for job outputs / uploads inside the container
ENV BILLING_DATA_DIR=/app/webapp

EXPOSE 8080

# Production WSGI server. Single process + threads keeps the in-memory job
# registry consistent (background jobs run as threads in this process).
CMD ["sh", "-c", "waitress-serve --listen=0.0.0.0:${PORT} --threads=8 app:app"]
