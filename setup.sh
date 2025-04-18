#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
# Load environment variables from .env file using a more robust method
if [ -f .env ]; then
    set -o allexport # Or 'set -a'
    source <(grep -v '^#' .env | sed -e '/^$/d') # Filter comments and empty lines
    set +o allexport # Or 'set +a'
else
    echo "Error: .env file not found!"
    exit 1
fi

# Extract DB details from DATABASE_URL (basic parsing, might need adjustment for complex URLs)
DB_NAME=$(echo $DATABASE_URL | awk -F/ '{print $NF}')
DB_USER=$(echo $DATABASE_URL | awk -F: '{print $2}' | awk -F@ '{print $1}' | sed 's|//||')
DB_HOST=$(echo $DATABASE_URL | awk -F@ '{print $2}' | awk -F: '{print $1}')
DB_PORT=$(echo $DATABASE_URL | awk -F: '{print $NF}' | awk -F/ '{print $1}')
# Note: Password extraction is omitted for security; psql/createdb should prompt or use ~/.pgpass

PYTHON_EXEC=".venv/bin/python"
PIP_EXEC=".venv/bin/pip"
MANAGE_PY="$PYTHON_EXEC manage.py"

echo "--- Lithographer CMS Initial Setup ---"

# --- Check Prerequisites ---
echo "Checking for Python virtual environment..."
if [ ! -d ".venv" ]; then
    echo "Virtual environment '.venv' not found. Please create it first (python3 -m venv .venv)"
    exit 1
fi
if [ ! -f "$PYTHON_EXEC" ]; then
    echo "Python executable not found in .venv/bin/"
    exit 1
fi

echo "Checking for PostgreSQL commands (psql, createdb)..."
if ! command -v psql &> /dev/null || ! command -v createdb &> /dev/null
then
    echo "Warning: psql or createdb command not found. Database setup might fail."
    echo "Ensure PostgreSQL client tools are installed and in your PATH."
    # Optionally exit here: exit 1
fi

# --- Database Setup ---
echo "Attempting to create database '$DB_NAME'..."
# Optional: Drop existing database first (use with caution!)
# dropdb --if-exists "$DB_NAME" -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" --echo || echo "Database '$DB_NAME' does not exist, continuing..."

# Create database - will likely ask for password if not configured via PGPASSWORD or ~/.pgpass
createdb "$DB_NAME" -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" --echo || echo "Database '$DB_NAME' might already exist or creation failed. Check PostgreSQL connection and credentials."

# --- Apply Migrations ---
echo "Applying database migrations..."
$MANAGE_PY migrate

# --- Create Superuser ---
echo "Creating superuser..."
# Set DJANGO_SUPERUSER_PASSWORD environment variable for non-interactive creation
# Ensure DJANGO_SUPERUSER_EMAIL and DJANGO_SUPERUSER_USERNAME (if needed) are set
# For interactive creation, remove the --noinput flag
# Example non-interactive (set these in .env or export them before running):
# export DJANGO_SUPERUSER_EMAIL=${DJANGO_SUPERUSER_EMAIL:-admin@example.com}
# export DJANGO_SUPERUSER_PASSWORD=${DJANGO_SUPERUSER_PASSWORD:-password} # CHANGE THIS!
# $MANAGE_PY createsuperuser --noinput --email "$DJANGO_SUPERUSER_EMAIL"
# echo "Superuser created with email: $DJANGO_SUPERUSER_EMAIL"

# Interactive creation:
echo "Please follow the prompts to create a superuser:"
$MANAGE_PY createsuperuser

# --- Optional: Load Initial Data ---
# echo "Loading initial data (e.g., default roles, permissions)..."
# $MANAGE_PY loaddata initial_roles.json initial_permissions.json

# --- Setup Complete ---
echo "-------------------------------------"
echo "Lithographer CMS setup script finished."
echo "You may need to:"
echo "1. Ensure PostgreSQL database '$DB_NAME' was created successfully."
echo "2. Verify the superuser was created."
echo "3. Start the development server: $MANAGE_PY runserver"
echo "-------------------------------------"

exit 0