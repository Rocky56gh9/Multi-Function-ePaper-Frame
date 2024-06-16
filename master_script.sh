#!/bin/bash

echo "Starting master_script.sh..."

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
chmod +x ~/multimode-epaper-frame/run_all_configs.py

# Change to the directory where run_all_configs.py is located
echo "Changing directory to ~/multimode-epaper-frame"
cd ~/multimode-epaper-frame || { echo "Failed to change directory to ~/multimode-epaper-frame. Exiting."; exit 1; }

# Output current directory to verify
echo "Current directory: $(pwd)"
ls -l

# Check if the flag file exists
if [ ! -f ~/multimode-epaper-frame/configs_executed.flag ]; then
  echo "Flag file does not exist. Running run_all_configs.py..."
  python3 run_all_configs.py

  # Check the exit status of run_all_configs.py
  if [ $? -ne 0 ]; then
    echo "run_all_configs.py encountered an error. Exiting."
    exit 1
  fi

  # Create a flag file to indicate the script has run
  echo "Creating flag file..."
  touch ~/multimode-epaper-frame/configs_executed.flag
else
  echo "Flag file exists. Skipping run_all_configs.py."
fi

echo "All configuration scripts have been executed successfully."
