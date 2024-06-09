import os

# Get the directory of the current script
script_dir = os.path.dirname(os.path.realpath(__file__))

# Path to the template files
DADJOKES_TEMPLATE_PATH = os.path.join(script_dir, '../templates/dadjokes_template.py')
SHOWERTHOUGHTS_TEMPLATE_PATH = os.path.join(script_dir, '../templates/showerthoughts_template.py')
WEATHERSTATION_TEMPLATE_PATH = os.path.join(script_dir, '../templates/weatherstation_template.py')

# Path to the script files
DADJOKES_SCRIPTS_PATH = os.path.join(script_dir, '../scripts/dadjokes.py')
SHOWERTHOUGHTS_SCRIPTS_PATH = os.path.join(script_dir, '../scripts/showerthoughts.py')
WEATHERSTATION_SCRIPTS_PATH = os.path.join(script_dir, '../scripts/weatherstation.py')

def configure_scripts():
    print("\nConfiguring Reddit Scripts")
    client_id = input("Enter your Reddit API client ID: ")
    client_secret = input("Enter your Reddit API client secret: ")
    user_agent = input("Enter your Reddit API user agent: ")

    home_dir = os.getenv("HOME")

    # Read the dadjokes template file
    with open(DADJOKES_TEMPLATE_PATH, 'r') as file:
        dadjokes_template_content = file.read()

    # Read the showerthoughts template file
    with open(SHOWERTHOUGHTS_TEMPLATE_PATH, 'r') as file:
        showerthoughts_template_content = file.read()

    # Replace placeholders with user inputs
    dadjokes_script_content = dadjokes_template_content.format(client_id=client_id, client_secret=client_secret, user_agent=user_agent, home_dir=home_dir)
    showerthoughts_script_content = showerthoughts_template_content.format(client_id=client_id, client_secret=client_secret, user_agent=user_agent, home_dir=home_dir)

    # Write the configured scripts to the scripts directory
    with open(DADJOKES_SCRIPTS_PATH, 'w') as file:
        file.write(dadjokes_script_content)

    with open(SHOWERTHOUGHTS_SCRIPTS_PATH, 'w') as file:
        file.write(showerthoughts_script_content)

    print(f"\nGenerated dad jokes script: {DADJOKES_SCRIPTS_PATH}")
    print(f"Generated shower thoughts script: {SHOWERTHOUGHTS_SCRIPTS_PATH}")

    print("\nConfiguring Weather Station Script")
    weather_api_key = input("Enter your OpenWeather API key: ")
    zip_code = input("Enter your zip code: ")
    country_code = input("Enter your country code: ")

    # Read the weatherstation template file
    with open(WEATHERSTATION_TEMPLATE_PATH, 'r') as file:
        weatherstation_template_content = file.read()

    # Replace placeholders with user inputs
    weatherstation_script_content = weatherstation_template_content.format(api_key=weather_api_key, zip_code=zip_code, country_code=country_code, home_dir=home_dir)

    # Write the configured script to the scripts directory
    with open(WEATHERSTATION_SCRIPTS_PATH, 'w') as file:
        file.write(weatherstation_script_content)

    print(f"Generated weather station script: {WEATHERSTATION_SCRIPTS_PATH}")

def main():
    print("\nScript Configuration Interface")
    configure_scripts()

if __name__ == "__main__":
    main()
