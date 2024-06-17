import os
import subprocess

# Define script mapping based on numerical input
script_map = {
    "1": "scripts/dadjokes.py",
    "2": "scripts/showerthoughts.py",
    "3": "scripts/weatherstation.py",
    "4": "horoscope"  # Horoscopes are handled separately
}

def configure_crontab():
    user = os.getenv('SUDO_USER', os.getenv('USER'))
    home_dir = os.path.expanduser(f"~{user}")
    project_path = os.path.join(home_dir, "multimode-epaper-frame")

    if not os.path.exists(project_path):
        print(f"Project path {project_path} does not exist. Please check the path.")
        return

    # Collecting environment variables
    sun_signs = os.getenv("SUN_SIGNS").split(',')
    script_top_hour = script_map[os.getenv("SCRIPT_TOP_HOUR")]
    script_quarter_past = script_map[os.getenv("SCRIPT_QUARTER_PAST")]
    script_half_past = script_map[os.getenv("SCRIPT_HALF_PAST")]
    script_quarter_to = script_map[os.getenv("SCRIPT_QUARTER_TO")]
    start_time = os.getenv("START_TIME")
    end_time = os.getenv("END_TIME")
    start_hour, start_minute = map(int, start_time.split(':'))
    end_hour, end_minute = map(int, end_time.split(':'))

    # Generate crontab lines
    cron_lines = []

    # Handle horoscope scheduling separately
    def schedule_horoscopes():
        for i, hour in enumerate(range(start_hour, end_hour + 1)):
            for sun_sign in sun_signs:
                script_path = f"{project_path}/scripts/horoscope_{sun_sign}.py"
                cron_lines.append(f"0 {hour} * * * /usr/bin/python3 {script_path}")

    # Schedule each script type
    schedule_horoscopes()  # Horoscope scheduling
    cron_lines.append(f"{start_minute} {start_hour} * * * /usr/bin/python3 {project_path}/{script_top_hour}")
    cron_lines.append(f"{end_minute} {end_hour} * * * /usr/bin/python3 {project_path}/scripts/sleep.py")

    # Write and install crontab
    crontab_file = os.path.join(project_path, "new_crontab")
    with open(crontab_file, "w") as file:
        file.write("# Generated crontab\n")
        file.writelines("\n".join(cron_lines))
    subprocess.run(["crontab", "-u", user, crontab_file])
    os.remove(crontab_file)
    print("Crontab configured successfully.")

if __name__ == "__main__":
    configure_crontab()
