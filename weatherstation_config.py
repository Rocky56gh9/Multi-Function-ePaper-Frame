import os

# Path to the template file
TEMPLATE_PATH = 'templates/weatherstation_template.py'
SCRIPTS_PATH = 'scripts/weatherstation.py'

def configure_weather():
    print("Configuring Weather Station Script")
    api_key = input("Enter your OpenWeather API key: ")
    zip_code = input("Enter your ZIP code: ")

    # Read the template file
    with open(TEMPLATE_PATH, 'r') as file:
        template_content = file.read()

    # Replace placeholders with user inputs
    script_content = template_content.format(api_key=api_key, zip_code=zip_code)

    # Write the configured script to the scripts directory
    with open(SCRIPTS_PATH, 'w') as file:
        file.write(script_content)

    print(f"Generated weather station script: {SCRIPTS_PATH}")

def main():
    print("Weather Station Configuration Interface")
    configure_weather()

if __name__ == "__main__":
    main()
