#!/bin/bash

# Ensure the script runs from the directory it resides in
cd "$(dirname "$0")"

echo "Welcome to the Project Setup!"
echo "Please enter the required information when prompted."

# General API information
read -p "Enter your Reddit API key: " REDDIT_API_KEY
export REDDIT_API_KEY
read -p "Enter your Reddit client secret: " REDDIT_CLIENT_SECRET
export REDDIT_CLIENT_SECRET
read -p "Enter your Reddit user agent: " REDDIT_USER_AGENT
export REDDIT_USER_AGENT
read -p "Enter your OpenWeather API key: " OPENWEATHER_API_KEY
export OPENWEATHER_API_KEY
read -p "Enter your ZIP code: " ZIP_CODE
export ZIP_CODE
read -p "Enter your country code (e.g., US): " COUNTRY_CODE
export COUNTRY_CODE

# Crontab configuration for script scheduling
echo "Available sun signs are: aquarius, aries, cancer, capricorn, gemini, leo, libra, pisces, sagittarius, scorpio, taurus, virgo"
read -p "Enter sun signs separated by commas (e.g., aquarius,aries,cancer): " SUN_SIGNS
export SUN_SIGNS

echo "Please specify the script to run at various times by entering the corresponding number:"
echo "1. Dad Jokes"
echo "2. Shower Thoughts"
echo "3. Weather"
echo "4. Horoscope (multiple horoscope scripts will be evenly distributed)"
read -p "Script for top of the hour (enter number, e.g., '1' for Dad Jokes): " SCRIPT_TOP_HOUR
export SCRIPT_TOP_HOUR
read -p "Script for quarter past the hour (enter number): " SCRIPT_QUARTER_PAST
export SCRIPT_QUARTER_PAST
read -p "Script for half past the hour (enter number): " SCRIPT_HALF_PAST
export SCRIPT_HALF_PAST
read -p "Script for quarter to the hour (enter number): " SCRIPT_QUARTER_TO
export SCRIPT_QUARTER_TO

# Timing for script execution
read -p "Enter start time for script execution (HH:MM, e.g., 07:00): " START_TIME
export START_TIME
read -p "Enter end time for script execution (HH:MM, e.g., 23:00): " END_TIME
export END_TIME

# Execute setup scripts
./setup_project.sh
python3 run_all_configs.py
python3 config/crontab_config.py  # Adjusted path to point to the config directory

echo "Setup completed successfully."
