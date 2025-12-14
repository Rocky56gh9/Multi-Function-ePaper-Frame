#!/usr/bin/env python3

import os

# Get the directory of the current script
script_dir = os.path.dirname(os.path.realpath(__file__))

# Path to the template files
DADJOKES_TEMPLATE_PATH = os.path.join(script_dir, "../templates/dadjokes_template.py")
SHOWERTHOUGHTS_TEMPLATE_PATH = os.path.join(script_dir, "../templates/showerthoughts_template.py")

# Path to the script files
DADJOKES_SCRIPTS_PATH = os.path.join(script_dir, "../scripts/dadjokes.py")
SHOWERTHOUGHTS_SCRIPTS_PATH = os.path.join(script_dir, "../scripts/showerthoughts.py")


def _inject_secrets(template: str, client_id: str, client_secret: str, user_agent: str, home_dir: str) -> str:
    """
    Only replace the known placeholders we intentionally put in the template.
    This avoids collisions with runtime f-strings like {top_post.title}.
    """
    return (
        template.replace("{client_id}", client_id)
        .replace("{client_secret}", client_secret)
        .replace("{user_agent}", user_agent)
        .replace("{home_dir}", home_dir)
    )


def configure_scripts():
    print("\nConfiguring Reddit Scripts")
    client_id = input("Enter your Reddit API client ID: ").strip()
    client_secret = input("Enter your Reddit API client secret: ").strip()
    user_agent = input("Enter your Reddit API user agent: ").strip()

    home_dir = os.getenv("HOME")
    if not home_dir:
        raise RuntimeError("HOME environment variable is not set.")

    # Read templates
    with open(DADJOKES_TEMPLATE_PATH, "r") as f:
        dadjokes_template_content = f.read()

    with open(SHOWERTHOUGHTS_TEMPLATE_PATH, "r") as f:
        showerthoughts_template_content = f.read()

    # Inject secrets safely (no .format())
    dadjokes_script_content = _inject_secrets(
        dadjokes_template_content, client_id, client_secret, user_agent, home_dir
    )
    showerthoughts_script_content = _inject_secrets(
        showerthoughts_template_content, client_id, client_secret, user_agent, home_dir
    )

    # Write scripts
    with open(DADJOKES_SCRIPTS_PATH, "w") as f:
        f.write(dadjokes_script_content)

    with open(SHOWERTHOUGHTS_SCRIPTS_PATH, "w") as f:
        f.write(showerthoughts_script_content)

    print(f"\nGenerated dad jokes script: {DADJOKES_SCRIPTS_PATH}")
    print(f"Generated shower thoughts script: {SHOWERTHOUGHTS_SCRIPTS_PATH}\n")


def main():
    print("\nScript Configuration Interface\n")
    configure_scripts()


if __name__ == "__main__":
    main()
