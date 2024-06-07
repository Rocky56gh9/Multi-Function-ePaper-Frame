import os
import subprocess

# List of all possible horoscope scripts
ALL_HOROSCOPE_SCRIPTS = [f"scripts/horoscope_{sun_sign}.py" for sun_sign in [
    "aries", "taurus", "gemini", "cancer",
    "leo", "virgo", "libra", "scorpio",
    "sagittarius", "capricorn", "aquarius", "pisces"
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

def get_wake_time():
    print("Specify the time to wake up the display (local time):")
    wake_time = input("Enter time in HH:MM format (24-hour clock, e.g., 07:00): ").strip()
    try:
        hours, minutes = map(int, wake_time.split(':'))
        if 0 <= hours < 24 and 0 <= minutes < 60:
            return f"{minutes} {hours} * * *"
    except ValueError:
        pass
    print("Invalid time format. Defaulting to 07:00 (7:00 AM).")
    return "0 7 * * *"  # Default to 07:00 (7:00 AM)

def get_sleep_time():
    print("Specify the time to put the display to sleep (local time):")
    sleep_time = input("Enter time in HH:MM format (24-hour clock, e.g., 22:00): ").strip()
    try:
        hours, minutes = map(int, sleep_time.split(':'))
        if 0 <= hours < 24 and 0 <= minutes < 60:
            return f"{minutes} {hours} * * *"
    except ValueError:
        pass
    print("Invalid time format. Defaulting to 22:00 (10:00 PM).")
    return "0 22 * * *"  # Default to 22:00 (10:00 PM)

def get_horoscope_sun_signs():
    print("Specify the sun signs for horoscopes you want to display (separated by spaces):")
    print("Valid sun signs are:")
    valid_sun_signs = [
        "aries", "taurus", "gemini", "cancer",
        "leo", "virgo", "libra", "scorpio",
        "sagittarius", "capricorn", "aquarius", "pisces"
    ]
    print(", ".join(valid_sun_signs))
    sun_signs = input("Enter the sun signs: ").strip().lower().split()
    return [f"scripts/horoscope_{sun_sign}.py" for sun_sign in sun_signs if sun_sign in valid_sun_signs]

def get_script_for_time(time_label):
    print(f"Specify the script to run at {time_label}:")
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

def configure_crontab():
    wake_time = get_wake_time()
    sleep_time = get_sleep_time()
    horoscope_scripts = get_horoscope_sun_signs()

    schedule = {
        "00": get_script_for_time("the top of the hour"),
        "15": get_script_for_time("15 past the hour"),
        "30": get_script_for_time("30 past the hour"),
        "45": get_script_for_time("45 past the hour"),
    }

    # Generate crontab lines
    cron_lines = []
    cron_lines.append(f"{wake_time} /usr/bin/python3 $HOME/multimode-epaper-frame/scripts/wake.py")

    for minute, script in schedule.items():
        if script == "horoscope":
            num_horoscope_scripts = len(horoscope_scripts)
            for i, horoscope_script in enumerate(horoscope_scripts):
                cron_lines.append(f"{minute} */{num_horoscope_scripts} * * * /usr/bin/python3 $HOME/multimode-epaper-frame/{horoscope_script}")
        else:
            cron_lines.append(f"{minute} * * * * /usr/bin/python3 $HOME/multimode-epaper-frame/{script}")

    cron_lines.append(f"{sleep_time} /usr/bin/python3 $HOME/multimode-epaper-frame/scripts/sleep.py")

    # Write the crontab file with headers and the new lines
    with open("new_crontab", "w") as file:
        file.write(CRONTAB_HEADER)
        file.write("\n")  # Add a blank line after the headers
        file.write("\n".join(cron_lines) + "\n")

    # Install the new crontab
    subprocess.run(["crontab", "new_crontab"])
    os.remove("new_crontab")
    print("Crontab configured successfully.")

def main():
    print("Crontab Configuration Interface")
    configure_crontab()

if __name__ == "__main__":
    main()
