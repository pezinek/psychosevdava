.PHONY: all venv run clean clean-data install-service enable-service disable-service remove-service

VENV_DIR = venv
PYTHON = $(VENV_DIR)/bin/python
PIP = $(VENV_DIR)/bin/pip
GUNICORN = $(VENV_DIR)/bin/gunicorn

# Assuming your Flask app instance is named 'app' in app.py
FLASK_APP_MODULE = app:app
APP_PORT = 8000 # Changed port

# --- Service Installation Variables ---
# IMPORTANT: Adjust PROJECT_ROOT and SERVICE_NAME to your actual setup on the Ubuntu server
PROJECT_ROOT = /var/www/psychosevdava # The absolute path to your project on the server
SERVICE_NAME = psychosevdava
SERVICE_FILE = $(SERVICE_NAME).service
GUNICORN_SCRIPT = gunicorn_start.sh
SYSTEMD_DIR = /etc/systemd/system

all: venv run

venv:
	@echo "Setting up virtual environment..."
	@test -d $(VENV_DIR) || python3 -m venv $(VENV_DIR)
	@echo "Installing dependencies..."
	@$(PIP) install --upgrade pip setuptools wheel
	@$(PIP) install -r requirements.txt

run: venv
	@echo "Running the application with Gunicorn on port $(APP_PORT)..."
	@$(GUNICORN) --bind 0.0.0.0:$(APP_PORT) $(FLASK_APP_MODULE)

clean: clean-data
	@echo "Cleaning up virtual environment..."
	@rm -rf $(VENV_DIR)
	@echo "Virtual environment removed."

clean-data:
	@echo "Cleaning up thumbnails and uploaded photos..."
	@find thumbnails/ -maxdepth 1 -mindepth 1 ! -name '.gitkeep' -exec rm -rf {} + 2>/dev/null || true
	@find uploaded_photos/ -maxdepth 1 -mindepth 1 ! -name '.gitkeep' -exec rm -rf {} + 2>/dev/null || true
	@echo "Thumbnails and uploaded photos cleaned."

# --- Systemd Service Targets ---

# This target requires sudo to copy the service file and script
install-service: $(GUNICORN_SCRIPT) $(SERVICE_FILE)
	@echo "Installing systemd service '$(SERVICE_NAME)'..."
	@echo "Ensure PROJECT_ROOT in Makefile and gunicorn_start.sh is correct: $(PROJECT_ROOT)"
	# Copy gunicorn_start.sh to the project root (must be executable)
	sudo cp $(GUNICORN_SCRIPT) $(PROJECT_ROOT)/$(GUNICORN_SCRIPT)
	sudo chmod +x $(PROJECT_ROOT)/$(GUNICORN_SCRIPT)
	# Copy service file to systemd directory
	sudo cp $(SERVICE_FILE) $(SYSTEMD_DIR)/$(SERVICE_FILE)
	@echo "Service file copied to $(SYSTEMD_DIR)/$(SERVICE_FILE)"
	@echo "Gunicorn startup script copied to $(PROJECT_ROOT)/$(GUNICORN_SCRIPT)"
	@echo "Service installation complete. Now run 'sudo make enable-service' to enable and start it."

# This target requires sudo to enable and start the service
enable-service:
	@echo "Enabling and starting systemd service '$(SERVICE_NAME)'..."
	sudo systemctl daemon-reload
	sudo systemctl enable $(SERVICE_FILE)
	sudo systemctl start $(SERVICE_FILE)
	sudo systemctl status $(SERVICE_FILE)

# This target requires sudo to stop and disable the service
disable-service:
	@echo "Stopping and disabling systemd service '$(SERVICE_NAME)'..."
	sudo systemctl stop $(SERVICE_FILE) || true # Use || true to prevent make from failing if service isn't running
	sudo systemctl disable $(SERVICE_FILE)
	@echo "Service '$(SERVICE_NAME)' stopped and disabled."

# This target requires sudo to remove the service file and script
remove-service: disable-service
	@echo "Removing systemd service files for '$(SERVICE_NAME)'..."
	sudo rm -f $(SYSTEMD_DIR)/$(SERVICE_FILE)
	sudo rm -f $(PROJECT_ROOT)/$(GUNICORN_SCRIPT)
	sudo systemctl daemon-reload
	@echo "Service files removed. You may need to clean logs manually if desired."

