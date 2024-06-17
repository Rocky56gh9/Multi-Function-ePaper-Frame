#!/bin/bash

echo "Starting master_script.sh..."

# Define URLs
SETUP_PROJECT_URL="https://raw.githubusercontent.com/Rocky56gh9/multimode-epaper-frame/main/setup_project.sh"
REPO_DIR="multimode-epaper-frame"
RUN_ALL_CONFIGS_SCRIPT="$REPO_DIR/run_all_configs.py"

# Download and run setup_project.sh
echo "Downloading setup_project.sh..."
curl -sL $SETUP_PROJECT_URL -o setup_project.sh

# Check if setup_project.sh was downloaded successfully
if [ ! -f setup_project.sh ]; then
  echo "Failed to download setup_project.sh. Exiting."
  exit 1
fi

# Make setup_project.sh executable
chmod +x setup_project.sh

# Run setup_project.sh
echo "Running setup_project.sh..."
./setup_project.sh

# Check the exit status of setup_project.sh
if [ $? -ne 0 ]; then
  echo "setup_project.sh encountered an error. Exiting."
  exit 1
fi

echo "setup_project.sh completed successfully."

# Ensure run_all_configs.py is executable
echo "Making run_all_configs.py executable..."
chmod +x $RUN_ALL_CONFIGS_SCRIPT

# Run the configuration scripts
echo "Running configuration scripts..."
python3 $RUN_ALL_CONFIGS_SCRIPT

# Check the exit status of run_all_configs.py
if [ $? -ne 0 ]; then
  echo "run_all_configs.py encountered an error. Exiting."
  exit 1
fi

echo "All configuration scripts have been executed successfully."
