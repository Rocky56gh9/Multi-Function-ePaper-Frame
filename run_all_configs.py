import os
import subprocess

def run_script(script_name):
    print(f"Running {script_name}...")
    subprocess.run(['python3', script_name], check=True)

scripts = [
    'config/dadjokes_showerthoughts_config.py',
    'config/weatherstation_config.py',
    'config/crontab_config.py'
]

for script in scripts:
    run_script(script)

print("All configuration scripts have been run.")
