#!/bin/bash

echo "Starting master_script.sh..."

# Define repository URL and local directory
REPO_URL="https://github.com/Rocky56gh9/multimode-epaper-frame.git"
LOCAL_DIR="multimode-epaper-frame"

# Clone the repository if it does not exist
if [ ! -d "$LOCAL_DIR" ]; then
  echo "Cloning repository from $REPO_URL..."
  git clone $REPO_URL
  if [ $? -ne 0 ]; then
    echo "Failed to clone repository. Exiting."
    exit 1
  fi
fi

# Change to the repository directory
cd $LOCAL_DIR || { echo "Failed to change directory to $LOCAL_DIR. Exiting."; exit 1; }

# Download setup_project.sh from the repository
echo "Downloading setup_project.sh..."
curl -sL https://raw.githubusercontent.com/Rocky56gh9/multimode-epaper-frame/main/setup_project.sh -o setup_project.sh

# Check if setup_project.sh was downloaded successfully
if [ ! -f setup_project.sh ]; then
  echo "Failed to download setup_project.sh. Exiting."
  exit 1
fi

# Make setup_project.sh executable
chmod +x setup_project.sh

# Run setup_project.sh and wait for it to complete
echo "Running setup_project.sh..."
bash setup_project.sh

# Check the exit status of setup_project.sh
if [ $? -ne 0 ]; then
  echo "setup_project.sh encountered an error. Exiting."
  exit 1
fi

echo "setup_project.sh completed successfully."

# Ensure run_all_configs.py is executable
echo "Making run_all_configs.py executable..."
chmod +x run_all_configs.py

# Output current directory to verify
echo "Current directory: $(pwd)"
ls -l

# Check if the flag file exists
if [ ! -f configs_executed.flag ]; then
  echo "Flag file does not exist. Running run_all_configs.py..."
  python3 run_all_configs.py

  # Check the exit status of run_all_configs.py
  if [ $? -ne 0 ]; then
    echo "run_all_configs.py encountered an error. Exiting."
    exit 1
  fi

  # Create a flag file to indicate the script has run
  echo "Creating flag file..."
  touch configs_executed.flag
else
  echo "Flag file exists. Skipping run_all_configs.py."
fi

echo "All configuration scripts have been executed successfully."
