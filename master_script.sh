#!/bin/bash

# Run setup_project.sh
bash setup_project.sh

# Ensure run_all_configs.py is executable
chmod +x ~/multimode-epaper-frame/run_all_configs.py

# Change to the directory where run_all_configs.py is located
cd ~/multimode-epaper-frame || exit

# Run the script
python3 run_all_configs.py

echo "All configuration scripts have been executed successfully."
