#!/usr/bin/env python3

import os
import subprocess

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# List of configuration scripts
scripts = [
    os.path.join(script_dir, "config/dadjokes_showerthoughts_config.py"),
    os.path.join(script_dir, "config/weatherstation_config.py"),
    os.path.join(script_dir, "config/crontab_config.py")
]

def run_script(script_path):
    try:
        subprocess.check_call(["python3", script_path])
        print(f"Completed {script_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running {script_path}: {e}")
        exit(1)

if __name__ == "__main__":
    for script in scripts:
        print(f"Running {script}...")
        run_script(script)
