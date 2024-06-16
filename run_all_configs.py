import os

def run_script(script_name):
    print(f"Running {script_name}...")
    os.system(f'python3 {script_name}')

scripts = [
    'config/dadjokes_showerthoughts_config.py',
    'config/weatherstation_config.py',
    'config/crontab_config.py'
]

for script in scripts:
    run_script(script)

print("All configuration scripts have been run.")
