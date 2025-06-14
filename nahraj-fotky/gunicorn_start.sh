#!/bin/bash

PROJECT_DIR="/var/www/psychosevdava/nahraj-fotky"
VENV_DIR="${PROJECT_DIR}/venv"
GUNICORN="${VENV_DIR}/bin/gunicorn"
FLASK_APP_MODULE="app:app" # Adjust if your Flask app instance is named differently
APP_PORT=5000 # Make sure this matches your Makefile or desired port

# Navigate to the project directory
cd "$PROJECT_DIR" || exit

# Activate the virtual environment
source "${VENV_DIR}/bin/activate"

# Run Gunicorn
exec "${GUNICORN}" --timeout 3600 --workers 3 --bind 127.0.0.1:"${APP_PORT}" "${FLASK_APP_MODULE}"

