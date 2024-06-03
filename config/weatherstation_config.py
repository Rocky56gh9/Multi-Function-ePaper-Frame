import os
import requests

# Get the directory of the current script
script_dir = os.path.dirname(os.path.realpath(__file__))

# Path to the template file
TEMPLATE_PATH = os.path.join(script_dir, '../templates/weatherstation_template.py')
SCRIPTS_PATH = os.path.join(script_dir, '../scripts/weatherstation.py')

def configure_weatherstation():
    print("Configuring Weather Station Script")
    api_key = input("Enter your OpenWeather API key: ")
    zip_code = input("Enter your ZIP code: ")
    
    home_dir = os.getenv("HOME")

    # Fetch location data
    location_url = f"http://api.openweathermap.org/data/2.5/weather?zip={zip_code},us&appid={api_key}"
    response = requests.get(location_url)
    if response.status_code == 200:
        data = response.json()
        lat = data['coord']['lat']
        lon = data['coord']['lon']
        temp = data['main']['temp']
        weather_description = data['weather'][0]['description']
    else:
        raise Exception("Error fetching location data")

    # Read the template file
    with open(TEMPLATE_PATH, 'r') as file:
        template_content = file.read()

    # Replace placeholders with user inputs
    script_content = template_content.format(api_key=api_key, zip_code=zip_code, home_dir=home_dir, lat=lat, lon=lon, temp=temp, weather_description=weather_description)

    # Write the configured script to the scripts directory
    with open(SCRIPTS_PATH, 'w') as file:
        file.write(script_content)

    print(f"Generated weather station script: {SCRIPTS_PATH}")

def main():
    print("Weather Station Configuration Interface")
    configure_weatherstation()

if __name__ == "__main__":
    main()
