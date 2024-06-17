import os
import subprocess

CRONTAB_HEADER = """# Edit this file to introduce tasks to be run by cron.
# 
# Each task to run has to be defined through a single line
# indicating with different fields when the task will be run
# and what command to run for the task
# 
# m h  dom mon dow   command
"""

# Map numerical input to script paths
script_map = {
    "1": "scripts/dadjokes.py",
    "2": "scripts/showerthoughts.py",
    "3": "scripts/weatherstation.py",
    "4": "horoscope"
}

def configure_crontab():
    user = os.getenv('SUDO_USER', os.getenv('USER'))
    home_dir = os.path.expanduser(f"~{user}")
    project_path = os.path.join(home_dir, "multimode-epaper-frame")
    
    # Check if the project path exists
    if not os.path.exists(project_path):
        print(f"Project path {project_path} does not exist. Please check the path.")
        return
    
    sun_signs = os.getenv("SUN_SIGNS").split(',')
    script_top_hour = script_map.get(os.getenv("SCRIPT_TOP_HOUR"))
    script_quarter_past = script_map.get(os.getenv("SCRIPT_QUARTER_PAST"))
    script_half_past = script_map.get(os.getenv("SCRIPT_HALF_PAST"))
    script_quarter_to = script_map.get(os.getenv("SCRIPT_QUARTER_TO"))

    # Generate crontab lines
    cron_lines = []
    
    # Function to handle script scheduling
    def handle_script_timing(minute, script_key):
        if script_key == "horoscope":
            for i, sun_sign in enumerate(sun_signs):
                horoscope_script = f"{project_path}/scripts/horoscope_{sun_sign}.py"
                cron_lines.append(f"{minute} * * * * /usr/bin/python3 {horoscope_script}")
        else:
            cron_lines.append(f"{minute} * * * * /usr/bin/python3 {project_path}/{script_key}")

    handle_script_timing("00", script_top_hour)
    handle_script_timing("15", script_quarter_past)
    handle_script_timing("30", script_half_past)
    handle_script_timing("45", script_quarter_to)

    # Write the crontab file with headers and the new lines
    crontab_file = os.path.join(project_path, "new_crontab")
    with open(crontab_file, "w") as file:
        file.write(CRONTAB_HEADER)
        file.write("\n".join(cron_lines) + "\n")

    # Install the new crontab for the correct user
    subprocess.run(["crontab", "-u", user, crontab_file], check=True)
    os.remove(crontab_file)
    print("Crontab configured successfully.")

if __name__ == "__main__":
    configure_crontab()
