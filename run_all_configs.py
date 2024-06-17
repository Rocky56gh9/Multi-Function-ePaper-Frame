import subprocess
import os

# List of configuration scripts to run
scripts = [
    'config/dadjokes_showerthoughts_config.py',
    'config/weatherstation_config.py',
    'config/crontab_config.py'
]

def check_environment_variables():
    required_vars = [
        "OPENWEATHER_API_KEY", 
        "ZIP_CODE", 
        "COUNTRY_CODE", 
        "REDDIT_CLIENT_ID", 
        "REDDIT_CLIENT_SECRET", 
        "REDDIT_USER_AGENT"
    ]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print("Missing environment variables:", ", ".join(missing_vars))
        exit(1)

def run_script(script_name):
    try:
        print(f"Running {script_name}...")
        subprocess.run(['python3', script_name], check=True)
        print(f"Completed {script_name}")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running {script_name}: {e}")
        return False
    return True

def main():
    check_environment_variables()

    flag_file = 'configs_executed.flag'
    if os.path.exists(flag_file):
        print(f"{flag_file} already exists. Exiting.")
        return

    failed_scripts = []
    for script in scripts:
        if not run_script(script):
            failed_scripts.append(script)

    if failed_scripts:
        print("The following scripts failed to execute correctly:")
        for script in failed_scripts:
            print(script)
        exit(1)

    # Create flag file to indicate scripts have been run
    with open(flag_file, 'w') as f:
        f.write("Configuration scripts executed.")
    
    print("All configuration scripts have been executed successfully.")

if __name__ == "__main__":
    main()
