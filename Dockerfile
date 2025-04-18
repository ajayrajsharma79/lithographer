# Dockerfile for Lithographer Django CMS

# ---- Builder Stage ----
# Use a specific Python version. Slim images are smaller.
FROM python:3.10-slim-buster AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Install system dependencies required for building Python packages
# libpq-dev is needed for psycopg2 (PostgreSQL adapter)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Copy only the requirements file first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
# Using --no-cache-dir reduces layer size
# Consider using a virtual environment here for better isolation,
# but installing globally is simpler for this stage if copying site-packages later.
RUN pip install --no-cache-dir -r requirements.txt


# ---- Final Stage ----
# Start from the same slim Python base image
FROM python:3.10-slim-buster

# Set environment variables (can be repeated, good practice)
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Install only runtime system dependencies
# libpq5 is the runtime library for PostgreSQL client
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user and group for security
RUN addgroup --system django-group && adduser --system --ingroup django-group django-user

# Copy installed Python packages from the builder stage
# This assumes dependencies were installed globally in the builder stage.
# Adjust the path if you used a virtual environment in the builder stage.
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy the application code into the container
COPY . .

# Collect static files
# Ensure STATIC_ROOT is correctly set in your Django settings.py
# Run this before changing ownership/user if STATIC_ROOT is outside /app owned by root initially
# Or ensure the target directory is writable by django-user
RUN python manage.py collectstatic --noinput

# Change ownership of the application directory to the non-root user
# Ensure the static files directory is also owned by the user if collected before this step
RUN chown -R django-user:django-group /app

# Switch to the non-root user
USER django-user

# Expose the port the app runs on
EXPOSE 8000

# --- IMPORTANT NOTES ---
# 1. Environment Variables:
#    - Configure sensitive settings (SECRET_KEY, DATABASE_URL, REDIS_URL, etc.)
#      using environment variables passed during container runtime (e.g., via docker-compose.yml or Kubernetes secrets).
#    - DO NOT hardcode secrets in this Dockerfile or your source code.
#
# 2. .dockerignore:
#    - Create a `.dockerignore` file in your project root to exclude files/directories
#      not needed in the image (e.g., .git, .venv, __pycache__, *.pyc, .env, local db files).
#      This speeds up builds and reduces image size. Example .dockerignore:
#      ```
#      __pycache__/
#      *.pyc
#      *.pyo
#      *.pyd
#      .Python
#      env/
#      venv/
#      .env*
#      .git/
#      .gitignore
#      db.sqlite3*
#      *.log
#      ```
#
# 3. Celery Worker:
#    - This Dockerfile is for the Django web application (Gunicorn).
#    - You will need a SEPARATE Dockerfile or service definition (in Docker Compose)
#      for your Celery worker(s). It can share much of the build process but
#      will have a different CMD, e.g.:
#      `CMD ["celery", "-A", "lithographer", "worker", "--loglevel=info"]`

# Run the application using Gunicorn
# Replace 'lithographer.wsgi:application' if your project structure differs.
# Adjust the number of workers based on your server resources.
CMD ["gunicorn", "lithographer.wsgi:application", "--bind", "0.0.0.0:8000", "--workers=3"]