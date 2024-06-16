import subprocess
import os

# List of configuration scripts to run
scripts = [
    'config/dadjokes_showerthoughts_config.py',
    'config/weatherstation_config.py',
    'config/crontab_config.py'
]

def run_script(script_name):
    try:
        print(f"Running {script_name}...")
        subprocess.run(['python3', script_name], check=True)
        print(f"Completed {script_name}")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running {script_name}: {e}")
        exit(1)

def main():
    flag_file = 'configs_executed.flag'
    if os.path.exists(flag_file):
        print(f"{flag_file} already exists. Exiting.")
        return

    for script in scripts:
        run_script(script)
    
    # Create flag file to indicate scripts have been run
    with open(flag_file, 'w') as f:
        f.write("Configuration scripts executed.")

    print("All configuration scripts have been executed successfully.")

if __name__ == "__main__":
    main()
