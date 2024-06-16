#!/bin/bash

# Run setup_project.sh and wait for it to complete
bash setup_project.sh

# Check the exit status of setup_project.sh
if [ $? -ne 0 ]; then
  echo "setup_project.sh encountered an error. Exiting."
  exit 1
fi

# Ensure run_all_configs.py is executable
chmod +x ~/multimode-epaper-frame/run_all_configs.py

# Change to the directory where run_all_configs.py is located
cd ~/multimode-epaper-frame || exit

# Output current directory to verify
echo "Current directory: $(pwd)"
ls -l

# Run the script
python3 run_all_configs.py

# Check the exit status of run_all_configs.py
if [ $? -ne 0 ]; then
  echo "run_all_configs.py encountered an error. Exiting."
  exit 1
fi

echo "All configuration scripts have been executed successfully."
