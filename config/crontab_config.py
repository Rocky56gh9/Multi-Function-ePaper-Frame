import os
import subprocess
import socket

# List of all possible horoscope scripts
ALL_HOROSCOPE_SCRIPTS = [f"scripts/horoscope_{sun_sign}.py" for sun_sign in [
    "aquarius", "aries", "cancer", "capricorn", "gemini", "leo", "libra", "pisces", "sagittarius", "scorpio", "taurus", "virgo"
]]

CRONTAB_HEADER = """# Edit this file to introduce tasks to be run by cron.
# 
# Each task to run has to be defined through a single line
# indicating with different fields when the task will be run
# and what command to run for the task
# 
# To define the time you can provide concrete values for
# minute (m), hour (h), day of month (dom), month (mon),
# and day of week (dow) or use '*' in these fields (for 'any').
# 
# Notice that tasks will be started based on the cron's system
# daemon's notion of time and timezones.
# 
# Output of the crontab jobs (including errors) is sent through
# email to the user the crontab file belongs to (unless redirected).
# 
# For example, you can run a backup of all your user accounts
# at 5 a.m every week with:
# 0 5 * * 1 tar -zcf /var/backups/home.tgz /home/
# 
# For more information see the manual pages of crontab(5) and cron(8)
# 
# m h  dom mon dow   command
"""

def get_horoscope_sun_signs():
    print("\n\nSpecify the sun signs for horoscopes you want to display (separated by spaces):")
    print("Valid sun signs are:")
    valid_sun_signs = [
        "aquarius", "aries", "cancer", "capricorn", "gemini", "leo", "libra", "pisces", "sagittarius", "scorpio", "taurus", "virgo"
    ]
    print(", ".join(valid_sun_signs))
    sun_signs = input("Enter the sun signs: ").strip().lower().split()
    return [f"scripts/horoscope_{sun_sign}.py" for sun_sign in sun_signs if sun_sign in valid_sun_signs]

def get_script_for_time(time_label):
    print(f"\n\nSpecify the script to run at {time_label}:")
    print("1. Dad Jokes")
    print("2. Shower Thoughts")
    print("3. Weather")
    print("4. Horoscope (multiple horoscope scripts will be evenly distributed)")
    choice = input("Enter the number of the script: ").strip()
    script_map = {
        "1": "scripts/dadjokes.py",
        "2": "scripts/showerthoughts.py",
        "3": "scripts/weatherstation.py",
        "4": "horoscope"  # Placeholder for horoscopes
    }
    return script_map.get(choice)

def get_time(prompt):
    print(f"\n\n{prompt}")
    time_input = input("Enter time in HH:MM format (24-hour clock, e.g., 14:30): ").strip()
    try:
        hours, minutes = map(int, time_input.split(':'))
        if 0 <= hours < 24 and 0 <= minutes < 60:
            return hours, minutes
    except ValueError:
        pass
    print("Invalid time format. Please enter the time in HH:MM format (24-hour clock).")
    return get_time(prompt)

def configure_crontab():
    # Determine the correct user and home directory
    user = os.getenv('SUDO_USER', os.getenv('USER'))
    home_dir = os.path.expanduser(f"~{user}")
    project_path = os.path.join(home_dir, "multimode-epaper-frame")
    
    # Ensure the project path is correct
    if not os.path.exists(project_path):
        print(f"Project path {project_path} does not exist. Please check the path.")
        return

    horoscope_scripts = get_horoscope_sun_signs()
    start_hour, start_minute = get_time("Specify the time to start running the scripts (local time):")
    sleep_hour, sleep_minute = get_time("Specify the time to display the sleep screen (local time):")

    schedule = {
        "00": get_script_for_time("the top of the hour"),
        "15": get_script_for_time("15 past the hour"),
        "30": get_script_for_time("30 past the hour"),
        "45": get_script_for_time("45 past the hour")
    }

    # Generate crontab lines
    cron_lines = []

    for minute, script in schedule.items():
        if script == "horoscope":
            total_hours = (sleep_hour - start_hour) + (1 if sleep_minute > start_minute else 0)
            interval_hours = total_hours // len(horoscope_scripts)
            current_hour = start_hour
            hour_list = list(range(start_hour, sleep_hour + 1))
            for idx, horoscope_script in enumerate(horoscope_scripts):
                for hour_offset in range(idx, len(hour_list), len(horoscope_scripts)):
                    job_hour = hour_list[hour_offset]
                    cron_lines.append(f"{minute} {job_hour} * * * /usr/bin/python3 {project_path}/{horoscope_script}")
        else:
            for hour in range(start_hour, sleep_hour):
                cron_lines.append(f"{minute} {hour} * * * /usr/bin/python3 {project_path}/{script}")

    cron_lines.append(f"{sleep_minute} {sleep_hour} * * * /usr/bin/python3 {project_path}/scripts/sleep.py")

    # Write the crontab file with headers and the new lines
    crontab_file = os.path.join(project_path, "new_crontab")
    with open(crontab_file, "w") as file:
        file.write(CRONTAB_HEADER)
        file.write("\n")  # Add a blank line after the headers
        file.write("\n".join(cron_lines) + "\n")

    # Install the new crontab for the correct user
    subprocess.run(["crontab", "-u", user, crontab_file], check=True)
    os.remove(crontab_file)
    print("Crontab configured successfully.")

def main():
    print("Crontab Configuration Interface")
    configure_crontab()

if __name__ == "__main__":
    main()
