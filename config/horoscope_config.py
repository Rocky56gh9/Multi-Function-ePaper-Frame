#!/usr/bin/env python3
import os
import json
import getpass

VALID_SIGNS = [
    "aries","taurus","gemini","cancer","leo","virgo","libra","scorpio",
    "sagittarius","capricorn","aquarius","pisces"
]

def main():
    home = os.getenv("HOME", "")
    project_dir = os.path.join(home, "multimode-epaper-frame")
    config_dir = os.path.join(project_dir, "config")
    os.makedirs(config_dir, exist_ok=True)

    secrets_path = os.path.join(config_dir, "secrets.json")
    schedule_path = os.path.join(config_dir, "horoscope_schedule.json")

    # Load existing secrets if present
    secrets = {}
    if os.path.exists(secrets_path):
        try:
            with open(secrets_path, "r") as f:
                secrets = json.load(f) or {}
        except Exception:
            secrets = {}

    key = getpass.getpass("Enter API Ninjas key for horoscopes (input hidden): ").strip()
    if not key:
        raise SystemExit("No key provided. Aborting.")
    secrets["API_NINJAS_KEY"] = key

    with open(secrets_path, "w") as f:
        json.dump(secrets, f, ensure_ascii=False, indent=2)
    try:
        os.chmod(secrets_path, 0o600)
    except Exception:
        pass

    print("Horoscope schedule configuration.")
    print("Choose mode:")
    print("  1) rotation  (hour-of-day cycles through a list of signs)")
    print("  2) hour_map  (explicit mapping of hour 0-23 to a sign)")
    mode_in = input("Mode [1/2] (default 1): ").strip() or "1"
    mode = "hour_map" if mode_in == "2" else "rotation"

    cfg = {"mode": mode}

    if mode == "rotation":
        raw = input("Enter signs in rotation order, comma-separated (e.g., scorpio,sagittarius,taurus): ").strip()
        signs = [s.strip().lower() for s in raw.split(",") if s.strip()]
        signs = [s for s in signs if s in VALID_SIGNS]
        if not signs:
            signs = ["scorpio"]
        cfg["signs"] = signs
    else:
        print("Enter mapping for hours you care about. Leave blank to skip an hour.")
        hours = {}
        for h in range(24):
            s = input(f"Hour {h:02d} sign (or blank): ").strip().lower()
            if not s:
                continue
            if s not in VALID_SIGNS:
                print(f"  Skipped invalid sign '{s}'.")
                continue
            hours[str(h)] = s
        if not hours:
            hours = {"0":"scorpio"}
        cfg["hours"] = hours
        cfg["hours"]["default"] = cfg["hours"].get("default", "scorpio")

    with open(schedule_path, "w") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
    print(f"Saved {secrets_path} and {schedule_path}")

if __name__ == "__main__":
    main()
