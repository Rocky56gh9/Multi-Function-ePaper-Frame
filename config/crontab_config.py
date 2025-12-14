#!/usr/bin/env python3

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

def get_script_for_time(time_label):
    print(f"\n\nSpecify the script to run at {time_label}:")
    print("1. Dad Jokes")
    print("2. Shower Thoughts")
    print("3. Weather")
    print("4. Horoscope (rotation configured via config/horoscope_schedule.json)")
    choice = input("Enter the number of the script: ").strip()
    script_map = {
        "1": "scripts/dadjokes.py",
        "2": "scripts/showerthoughts.py",
        "3": "scripts/weatherstation.py",
        "4": "scripts/horoscope_display.py",
    }
    return script_map.get(choice)

def get_time(prompt):
    print(f"\n\n{prompt}")
    time_input = input("Enter time in HH:MM format (24-hour clock, e.g., 14:30): ").strip()
    try:
        hours, minutes = map(int, time_input.split(":"))
        if 0 <= hours < 24 and 0 <= minutes < 60:
            return hours, minutes
    except ValueError:
        pass
    print("Invalid time format. Please enter the time in HH:MM format (24-hour clock).")
    return get_time(prompt)

def _build_hours_list(start_hour, start_minute, sleep_hour, sleep_minute):
    """
    Returns list of hours to schedule jobs for a given minute slot, ensuring we do not run at/after sleep time.
    Rule:
      - If sleep_minute == 0, do not schedule any jobs in sleep_hour (sleep starts exactly at that hour).
      - If sleep_minute > 0, allow jobs in sleep_hour only for minutes < sleep_minute.
    This function returns the hours for which jobs at the given minute are allowed, but it does NOT know the minute yet.
    We'll filter again per-minute.
    """
    # Always include start_hour
    if (sleep_hour, sleep_minute) <= (start_hour, start_minute):
        # If user config is weird (sleep before start), default to start..start
        return [start_hour]

    return list(range(start_hour, sleep_hour + 1))

def configure_crontab():
    # Determine the correct user and home directory
    user = os.getenv("SUDO_USER", os.getenv("USER"))
    home_dir = os.path.expanduser(f"~{user}")
    project_path = os.path.join(home_dir, "multimode-epaper-frame")

    if not os.path.exists(project_path):
        print(f"Project path {project_path} does not exist. Please check the path.")
        return

    start_hour, start_minute = get_time("Specify the time to start running the scripts (local time):")
    sleep_hour, sleep_minute = get_time("Specify the time to display the sleep screen (local time):")

    schedule = {
        "00": get_script_for_time("the top of the hour"),
        "15": get_script_for_time("15 past the hour"),
        "30": get_script_for_time("30 past the hour"),
        "45": get_script_for_time("45 past the hour"),
    }

    # Build cron lines
    cron_lines = []
    hours_list = _build_hours_list(start_hour, start_minute, sleep_hour, sleep_minute)

    for minute_str, script in schedule.items():
        if not script:
            continue

        minute = int(minute_str)

        for hour in hours_list:
            # Do not schedule jobs before the start time on the start hour
            if hour == start_hour and minute < start_minute:
                continue

            # Do not schedule jobs at/after sleep time on the sleep hour
            if hour == sleep_hour:
                # If sleep is at HH:MM, then any job at HH:minute where minute >= sleep_minute must not run
                if minute >= sleep_minute:
                    continue

            cron_lines.append(f"{minute_str} {hour} * * * /usr/bin/python3 {project_path}/{script}")

    # Sleep screen itself (exact time)
    cron_lines.append(f"{sleep_minute} {sleep_hour} * * * /usr/bin/python3 {project_path}/scripts/sleep.py")

    # Write and install crontab
    crontab_file = os.path.join(project_path, "new_crontab")
    with open(crontab_file, "w") as file:
        file.write(CRONTAB_HEADER)
        file.write("\n")
        file.write("\n".join(cron_lines) + "\n")

    subprocess.run(["crontab", "-u", user, crontab_file], check=True)
    os.remove(crontab_file)
    print("Crontab configured successfully.")

def main():
    print("Crontab Configuration Interface")
    configure_crontab()

if __name__ == "__main__":
    main()
