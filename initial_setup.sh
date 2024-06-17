#!/bin/bash

# Install Git if not already installed
if ! command -v git &> /dev/null
then
    echo "Git could not be found, installing Git..."
    sudo apt-get update && sudo apt-get install -y git
else
    echo "Git is already installed."
fi

# Ensure the script runs from the directory it resides in
cd "$(dirname "$0")"

echo "Welcome to the Project Setup!"
echo "Please enter the required information when prompted."

# Collect information
read -p "Enter your Reddit API key: " REDDIT_API_KEY
read -p "Enter your Reddit client secret: " REDDIT_CLIENT_SECRET
read -p "Enter your Reddit user agent: " REDDIT_USER_AGENT
read -p "Enter your OpenWeather API key: " OPENWEATHER_API_KEY
read -p "Enter your ZIP code: " ZIP_CODE
read -p "Enter your country code (e.g., US): " COUNTRY_CODE
read -p "Enter sun signs separated by commas (e.g., aquarius,aries,cancer): " SUN_SIGNS

# Environment variables exportation for current session
export REDDIT_API_KEY REDDIT_CLIENT_SECRET REDDIT_USER_AGENT OPENWEATHER_API_KEY
export ZIP_CODE COUNTRY_CODE SUN_SIGNS

# Clone the repository
echo "Cloning the project repository..."
git clone https://github.com/Rocky56gh9/multimode-epaper-frame.git
cd multimode-epaper-frame

# Execute setup scripts
echo "Running setup scripts..."
bash setup_project.sh
python3 run_all_configs.py
python3 config/crontab_config.py

echo "Setup completed successfully."
