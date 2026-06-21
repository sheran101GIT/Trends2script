# Use the official Python image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install system dependencies (needed for some Python packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# CRASH-06: Ensure output/ and instance/ directories exist and are writable
RUN mkdir -p /app/output /app/instance && chmod 777 /app/output /app/instance

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Expose the port the app runs on
EXPOSE 5000

# CRASH-04: Use 1 worker for SQLite compatibility (avoids "database is locked" errors).
# For a PostgreSQL database, this can safely be increased to 3+.
# --timeout 120 allows long-running pipelines to complete without premature worker kill.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "4", "--timeout", "120", "app:app"]
