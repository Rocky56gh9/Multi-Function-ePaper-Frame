#!/usr/bin/env python3

import subprocess

# List of configuration scripts to run
scripts = [
    'config/dadjokes_showerthoughts_config.py',
    'config/weatherstation_config.py',
    'config/crontab_config.py'
]

def run_script(script_name):
    try:
        subprocess.run(['python3', script_name], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running {script_name}: {e}")
        exit(1)

def main():
    for script in scripts:
        print(f"Running {script}...")
        run_script(script)
        print(f"Completed {script}")

if __name__ == "__main__":
    main()
