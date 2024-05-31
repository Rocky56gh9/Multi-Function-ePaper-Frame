import os

# Path to the template file
TEMPLATE_PATH = 'templates/dadjokes_template.py'
SCRIPTS_PATH = 'scripts/dadjokes.py'

def configure_dadjokes():
    print("Configuring Dad Jokes Script")
    client_id = input("Enter your Reddit API client ID: ")
    client_secret = input("Enter your Reddit API client secret: ")
    user_agent = input("Enter your Reddit API user agent: ")

    # Read the template file
    with open(TEMPLATE_PATH, 'r') as file:
        template_content = file.read()

    # Replace placeholders with user inputs
    script_content = template_content.format(client_id=client_id, client_secret=client_secret, user_agent=user_agent)

    # Write the configured script to the scripts directory
    with open(SCRIPTS_PATH, 'w') as file:
        file.write(script_content)

    print(f"Generated dad jokes script: {SCRIPTS_PATH}")

def main():
    print("Dad Jokes Configuration Interface")
    configure_dadjokes()

if __name__ == "__main__":
    main()
