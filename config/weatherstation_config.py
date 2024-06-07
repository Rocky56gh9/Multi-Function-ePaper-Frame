import os

def populate_template(template_path, output_path, variables):
    with open(template_path, 'r') as file:
        template_content = file.read()

    for key, value in variables.items():
        template_content = template_content.replace(f'{{{key}}}', value)

    with open(output_path, 'w') as file:
        file.write(template_content)

def main():
    api_key = input("Enter your OpenWeather API key: ")
    zip_code = input("Enter the zip code: ")
    country_code = input("Enter the country code (e.g., US for United States): ")

    variables = {
        'API_KEY': api_key,
        'ZIP_CODE': zip_code,
        'COUNTRY_CODE': country_code
    }

    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(script_dir, '../templates/weatherstation_template.py')
    output_path = os.path.join(script_dir, '../scripts/weatherstation.py')

    populate_template(template_path, output_path, variables)
    print("weatherstation.py has been created in the scripts folder.")

if __name__ == "__main__":
    main()
