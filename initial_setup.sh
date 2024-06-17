#!/bin/bash

# Install Git if not already installed
if ! command -v git &> /dev/null; then
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
read -p "Enter your Reddit API client ID: " REDDIT_CLIENT_ID
read -p "Enter your Reddit client secret: " REDDIT_CLIENT_SECRET
read -p "Enter your Reddit user agent: " REDDIT_USER_AGENT
read -p "Enter your OpenWeather API key: " OPENWEATHER_API_KEY
read -p "Enter your ZIP code: " ZIP_CODE
read -p "Enter your country code (e.g., US): " COUNTRY_CODE
read -p "Enter sun signs separated by commas (e.g., aquarius,aries,cancer): " SUN_SIGNS

# Export environment variables for current session
export REDDIT_CLIENT_ID REDDIT_API_KEY REDDIT_CLIENT_SECRET REDDIT_USER_AGENT OPENWEATHER_API_KEY ZIP_CODE COUNTRY_CODE SUN_SIGNS

# Additional variables for crontab_config.py
echo "Please select the scripts to run at specified times:"
echo "1. Dad Jokes"
echo "2. Shower Thoughts"
echo "3. Weather"
echo "4. Horoscope"

read -p "Enter the number of the script to run at the top of the hour: " SCRIPT_TOP_HOUR_NUM
read -p "Enter the number of the script to run at 15 past the hour: " SCRIPT_15_MIN_NUM
read -p "Enter the number of the script to run at 30 past the hour: " SCRIPT_30_MIN_NUM
read -p "Enter the number of the script to run at 45 past the hour: " SCRIPT_45_MIN_NUM

case $SCRIPT_TOP_HOUR_NUM in
    1) SCRIPT_TOP_HOUR="scripts/dadjokes.py" ;;
    2) SCRIPT_TOP_HOUR="scripts/showerthoughts.py" ;;
    3) SCRIPT_TOP_HOUR="scripts/weatherstation.py" ;;
    4) SCRIPT_TOP_HOUR="scripts/horoscope.py" ;;
    *) echo "Invalid selection for top of the hour script." ; exit 1 ;;
esac

case $SCRIPT_15_MIN_NUM in
    1) SCRIPT_15_MIN="scripts/dadjokes.py" ;;
    2) SCRIPT_15_MIN="scripts/showerthoughts.py" ;;
    3) SCRIPT_15_MIN="scripts/weatherstation.py" ;;
    4) SCRIPT_15_MIN="scripts/horoscope.py" ;;
    *) echo "Invalid selection for 15 past the hour script." ; exit 1 ;;
esac

case $SCRIPT_30_MIN_NUM in
    1) SCRIPT_30_MIN="scripts/dadjokes.py" ;;
    2) SCRIPT_30_MIN="scripts/showerthoughts.py" ;;
    3) SCRIPT_30_MIN="scripts/weatherstation.py" ;;
    4) SCRIPT_30_MIN="scripts/horoscope.py" ;;
    *) echo "Invalid selection for 30 past the hour script." ; exit 1 ;;
esac

case $SCRIPT_45_MIN_NUM in
    1) SCRIPT_45_MIN="scripts/dadjokes.py" ;;
    2) SCRIPT_45_MIN="scripts/showerthoughts.py" ;;
    3) SCRIPT_45_MIN="scripts/weatherstation.py" ;;
    4) SCRIPT_45_MIN="scripts/horoscope.py" ;;
    *) echo "Invalid selection for 45 past the hour script." ; exit 1 ;;
esac

export SCRIPT_TOP_HOUR SCRIPT_15_MIN SCRIPT_30_MIN SCRIPT_45_MIN

# Prompt for start and end times for the schedule
read -p "Specify the start time to run the scripts (in HH:MM format, e.g., 07:00): " START_TIME
read -p "Specify the end time to stop running the scripts (in HH:MM format, e.g., 23:00): " END_TIME

export START_TIME END_TIME

# Clone the repository if it doesn't exist
REPO_DIR="multimode-epaper-frame"
if [ -d "$REPO_DIR" ]; then
    echo "The directory '$REPO_DIR' already exists. Skipping clone."
else
    echo "Cloning the project repository..."
    git clone https://github.com/Rocky56gh9/multimode-epaper-frame.git
fi
cd $REPO_DIR

# Clone the e-Paper repository into the multimode-epaper-frame directory
if [ -d "e-Paper" ]; then
    echo "The directory 'e-Paper' already exists. Skipping clone."
else
    echo "Cloning the e-Paper repository..."
    git clone https://github.com/waveshare/e-Paper.git
fi

# Execute setup scripts
echo "Running setup scripts..."
bash setup_project.sh

python3 run_all_configs.py
python3 config/crontab_config.py

echo "Setup completed successfully."
