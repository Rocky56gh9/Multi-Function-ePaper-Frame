#!/bin/bash

# Step 0: Ensure git and python3 are installed
sudo apt-get update
sudo apt-get install -y git python3

# Define the GitHub repository URL
REPO_URL="https://github.com/Rocky56gh9/multimode-epaper-frame.git"
REPO_DIR="multimode-epaper-frame"

# Step 1: Clone the repository
git clone $REPO_URL
echo "Repository cloned successfully."

# Step 2: Navigate to the repository directory
cd $REPO_DIR

# Step 3: Run the setup_project.sh script
echo "Starting setup..."
./setup_project.sh
echo "Setup completed successfully."

# Step 4: Run the run_all_configs.py Python script interactively
echo "Starting configuration..."
python3 run_all_configs.py
echo "Configuration completed successfully."
