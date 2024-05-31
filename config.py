import os

# Define file paths
WEATHER_FILE = 'scripts/weatherstation.py'
DADJOKES_FILE = 'scripts/dadjokes.py'
SHOWERTHOUGHTS_FILE = 'scripts/showerthoughts.py'
HOROSCOPE_FILE = 'scripts/horoscope.py'

def update_file(file_path, variable, value):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    with open(file_path, 'w') as file:
        for line in lines:
            if line.strip().startswith(variable):
                file.write(f'{variable} = "{value}"\n')
            else:
                file.write(line)

def configure_weather():
    print("Configuring Weather Station Script")
    api_key = input("Enter your OpenWeather API key: ")
    zip_code = input("Enter your ZIP code: ")
    update_file(WEATHER_FILE, 'api_key', api_key)
    update_file(WEATHER_FILE, 'zip_code', zip_code)

def configure_dadjokes():
    print("Configuring Dad Jokes Script")
    client_id = input("Enter your Reddit API client ID: ")
    client_secret = input("Enter your Reddit API client secret: ")
    user_agent = input("Enter your Reddit API user agent: ")
    update_file(DADJOKES_FILE, 'client_id', client_id)
    update_file(DADJOKES_FILE, 'client_secret', client_secret)
    update_file(DADJOKES_FILE, 'user_agent', user_agent)

def configure_showerthoughts():
    print("Configuring Shower Thoughts Script")
    client_id = input("Enter your Reddit API client ID: ")
    client_secret = input("Enter your Reddit API client secret: ")
    user_agent = input("Enter your Reddit API user agent: ")
    update_file(SHOWERTHOUGHTS_FILE, 'client_id', client_id)
    update_file(SHOWERTHOUGHTS_FILE, 'client_secret', client_secret)
    update_file(SHOWERTHOUGHTS_FILE, 'user_agent', user_agent)

def configure_horoscope():
    print("Configuring Horoscope Script")
    sunsign = input("Enter your sun sign: ")
    with open(HOROSCOPE_FILE, 'r') as file:
        lines = file.readlines()
    with open(HOROSCOPE_FILE, 'w') as file:
        for line in lines:
            if line.strip().startswith('sunsign'):
                file.write(f'sunsign = "{sunsign}"\n')
            else:
                file.write(line)

def main():
    print("Configuration Interface")
    print("1. Configure Weather Station")
    print("2. Configure Dad Jokes")
    print("3. Configure Shower Thoughts")
    print("4. Configure Horoscope")
    print("5. Exit")
    
    choice = input("Select an option: ")
    if choice == '1':
        configure_weather()
    elif choice == '2':
        configure_dadjokes()
    elif choice == '3':
        configure_showerthoughts()
    elif choice == '4':
        configure_horoscope()
    elif choice == '5':
        exit()
    else:
        print("Invalid option. Please select a valid option.")
        main()

if __name__ == "__main__":
    main()
