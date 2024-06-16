#!/bin/bash

# Ensure the scripts are executable
chmod +x config/*.py

# Change to the config directory
cd config || exit

# Run each configuration script sequentially
echo "Running dadjokes_showerthoughts_config.py..."
python3 dadjokes_showerthoughts_config.py
echo "Completed dadjokes_showerthoughts_config.py"

echo "Running weatherstation_config.py..."
python3 weatherstation_config.py
echo "Completed weatherstation_config.py"

echo "Running crontab_config.py..."
python3 crontab_config.py
echo "Completed crontab_config.py"

echo "All configuration scripts have been run."
