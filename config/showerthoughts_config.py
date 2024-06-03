import os

# Path to the template file
TEMPLATE_PATH = 'templates/showerthoughts_template.py'
SCRIPTS_PATH = 'scripts/showerthoughts.py'

def configure_showerthoughts():
    print("Configuring Shower Thoughts Script")
    client_id = input("Enter your Reddit API client ID: ")
    client_secret = input("Enter your Reddit API client secret: ")
    user_agent = input("Enter your Reddit API user agent: ")
    
    home_dir = os.getenv("HOME")

    # Read the template file
    with open(TEMPLATE_PATH, 'r') as file:
        template_content = file.read()

    # Replace placeholders with user inputs
    script_content = template_content.format(client_id=client_id, client_secret=client_secret, user_agent=user_agent, home_dir=home_dir)

    # Write the configured script to the scripts directory
    with open(SCRIPTS_PATH, 'w') as file:
        file.write(script_content)

    print(f"Generated shower thoughts script: {SCRIPTS_PATH}")

def main():
    print("Shower Thoughts Configuration Interface")
    configure_showerthoughts()

if __name__ == "__main__":
    main()
