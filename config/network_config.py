import os
import subprocess
import time
import logging

# Configure logging
logging.basicConfig(filename='/var/log/wifi_config.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s:%(message)s')

def log_and_print(message):
    print(message)
    logging.info(message)

def log_debug(message):
    logging.debug(message)

def run_command(command, retries=3, delay=5):
    for attempt in range(retries):
        try:
            subprocess.run(command, check=True)
            return True
        except subprocess.CalledProcessError as e:
            log_and_print(f"Command failed: {e}. Retrying ({attempt + 1}/{retries})...")
            time.sleep(delay)
    return False

def list_known_networks():
    wifi_conf_path = '/etc/wpa_supplicant/wpa_supplicant.conf'
    networks = []
    with open(wifi_conf_path, 'r') as file:
        lines = file.readlines()
        for i, line in enumerate(lines):
            if 'ssid=' in line:
                ssid = line.strip().split('=')[1].strip('"')
                networks.append((i, ssid))
    log_debug(f"Networks found: {networks}")
    return networks, lines

def display_known_networks():
    networks, _ = list_known_networks()
    if networks:
        log_and_print("\nKnown Networks:")
        for idx, (line_num, ssid) in enumerate(networks):
            log_and_print(f"{idx + 1}. {ssid}")
    else:
        log_and_print("\nNo known networks found.")

def update_or_remove_network():
    while True:
        networks, lines = list_known_networks()
        if not networks:
            log_and_print("No known networks to update or remove.")
            return

        display_known_networks()
        log_and_print(f"{len(networks) + 1}. Back")
        choice = int(input("\nEnter the number of the network to update/remove: ")) - 1
        if choice == len(networks):
            return
        if choice < 0 or choice >= len(networks):
            log_and_print("Invalid selection.")
            continue

        _, ssid = networks[choice]
        log_and_print(f"\nSelected network: {ssid}")
        log_and_print("1. Update password")
        log_and_print("2. Remove network")
        log_and_print("3. Back")
        action = int(input("Select an option: "))

        if action == 1:
            new_psk = input("Enter the new password: ").strip()
            update_network_password(lines, networks[choice][0], new_psk)
        elif action == 2:
            if len(networks) > 1:
                remove_network(lines, networks[choice][0])
            else:
                log_and_print("Cannot remove the last known network.")
        elif action == 3:
            return
        else:
            log_and_print("Invalid option.")

def update_network_password(lines, line_num, new_psk):
    log_debug(f"Updating password for network at line {line_num}")
    for i in range(line_num, len(lines)):
        if 'psk=' in lines[i]:
            log_debug(f"Updating psk at line {i}")
            lines[i] = f'    psk="{new_psk}"\n'
            break

    write_wifi_conf(lines)
    log_and_print("Network password updated.")
    reboot_device()

def remove_network(lines, line_num):
    log_debug(f"Removing network block starting at line {line_num}")
    start, end = None, None
    for i in range(line_num, -1, -1):
        if 'network={' in lines[i]:
            start = i
            log_debug(f"Found network start at line {start}")
            break

    for i in range(line_num, len(lines)):
        if '}' in lines[i]:
            end = i
            log_debug(f"Found network end at line {end}")
            break

    if start is not None and end is not None:
        del lines[start:end + 1]
        log_debug(f"Removed lines {start} to {end}")
        write_wifi_conf(lines)
        log_and_print("Network removed.")
        reboot_device()
    else:
        log_and_print("Failed to locate the network block in the configuration file.")
        log_debug(f"Failed to locate network block starting at line {line_num}")

def write_wifi_conf(lines):
    wifi_conf_path = '/etc/wpa_supplicant/wpa_supplicant.conf'
    with open(wifi_conf_path, 'w') as file:
        file.writelines(lines)
    log_debug("Updated wpa_supplicant.conf written")

def reboot_device():
    log_and_print("Rebooting device to apply changes...")
    time.sleep(5)
    run_command(["sudo", "reboot"])

def restart_network_services():
    log_and_print("\nRestarting network services...\n")
    if run_command(["sudo", "systemctl", "restart", "dhcpcd"]):
        log_and_print("Network services restarted.")
        log_and_print("Please wait a few moments for the network to stabilize.")
        log_and_print("If you lose connection, please reconnect or open a new terminal window.")
        time.sleep(10)  # Give time for the user to read the message
        log_and_print("Returning to the main menu...")
    else:
        log_and_print("Failed to restart network services.")

def configure_wifi():
    log_and_print("\nWiFi Configuration\n")
    add_wifi_settings()

def add_wifi_settings():
    ssid = input("\nEnter your WiFi SSID: ").strip()
    psk = input("Enter your WiFi password: ").strip()

    # Avoid duplicate SSIDs
    networks, lines = list_known_networks()
    if any(ssid == network_ssid for _, network_ssid in networks):
        log_and_print(f"Network {ssid} already exists. Updating password instead.")
        for i, (_, network_ssid) in enumerate(networks):
            if network_ssid == ssid:
                update_network_password(lines, networks[i][0], psk)
                return

    wifi_conf_path = '/etc/wpa_supplicant/wpa_supplicant.conf'
    backup_wifi_conf_path = '/etc/wpa_supplicant/wpa_supplicant.conf.bak'

    if not run_command(["sudo", "cp", wifi_conf_path, backup_wifi_conf_path]):
        log_and_print("Failed to create backup of WiFi configuration. Aborting.")
        exit(1)

    log_and_print("\nBackup of current WiFi configuration created.\n")

    wifi_conf = f"""
network={{
    ssid="{ssid}"
    psk="{psk}"
}}
"""
    try:
        with open(wifi_conf_path, 'a') as file:
            file.write(wifi_conf)
        log_and_print("\nNew WiFi settings added.\n")
    except PermissionError:
        log_and_print("Permission denied. Please run this script with sudo.")
        exit(1)

    log_debug(f"Attempting to connect to new network {ssid} with password {psk}")
    attempt_wifi_connection(ssid, backup_wifi_conf_path)

def attempt_wifi_connection(ssid, backup_wifi_conf_path):
    restart_network_services()
    log_and_print("\nTesting connection to the new WiFi network. This will take up to 30 seconds...")
    time.sleep(30)

    result = subprocess.run(["sudo", "iwgetid"], capture_output=True, text=True)
    log_debug(f"iwgetid result: {result.stdout}")
    if ssid in result.stdout:
        log_and_print(f"\nSuccessfully connected to {ssid}\n")
        reboot_device()
    else:
        log_and_print(f"\nFailed to connect to {ssid}. Reverting to previous WiFi settings...\n")
        revert_to_backup(backup_wifi_conf_path)

    log_and_print("\nConfiguration complete. You may now close this terminal.\n")

def revert_to_backup(backup_wifi_conf_path):
    wifi_conf_path = '/etc/wpa_supplicant/wpa_supplicant.conf'
    if not run_command(["sudo", "cp", backup_wifi_conf_path, wifi_conf_path]):
        log_and_print("Failed to revert to backup WiFi settings. Manual intervention required.")
        exit(1)

    log_and_print("\nBackup restored successfully.")
    reboot_device()

def preserve_gadget_mode():
    log_and_print("\nPreserving gadget mode settings...\n")
    if not run_command(["sudo", "modprobe", "libcomposite"]):
        log_and_print("Failed to load libcomposite module.")
        return

    gadget_dir = "/sys/kernel/config/usb_gadget/g1"
    if os.path.exists(gadget_dir):
        run_command(["sudo", "rm", "-rf", gadget_dir])

    if not run_command(["sudo", "mkdir", "-p", gadget_dir]):
        log_and_print("Failed to create gadget directory.")
        return

    commands = [
        ['sudo', 'bash', '-c', 'echo 0x1d6b > /sys/kernel/config/usb_gadget/g1/idVendor'],
        ['sudo', 'bash', '-c', 'echo 0x0104 > /sys/kernel/config/usb_gadget/g1/idProduct'],
        ['sudo', 'bash', '-c', 'echo 0x0100 > /sys/kernel/config/usb_gadget/g1/bcdDevice'],
        ['sudo', 'bash', '-c', 'echo 0x0200 > /sys/kernel/config/usb_gadget/g1/bcdUSB'],
        ['sudo', 'mkdir', '-p', '/sys/kernel/config/usb_gadget/g1/strings/0x409'],
        ['sudo', 'bash', '-c', 'echo "fedcba9876543210" > /sys/kernel/config/usb_gadget/g1/strings/0x409/serialnumber'],
        ['sudo', 'bash', '-c', 'echo "Manufacturer" > /sys/kernel/config/usb_gadget/g1/strings/0x409/manufacturer'],
        ['sudo', 'bash', '-c', 'echo "Product" > /sys/kernel/config/usb_gadget/g1/strings/0x409/product'],
        ['sudo', 'mkdir', '-p', '/sys/kernel/config/usb_gadget/g1/configs/c.1/strings/0x409'],
        ['sudo', 'bash', '-c', 'echo "Config 1: ECM network" > /sys/kernel/config/usb_gadget/g1/configs/c.1/strings/0x409/configuration'],
        ['sudo', 'bash', '-c', 'echo 250 > /sys/kernel/config/usb_gadget/g1/configs/c.1/MaxPower'],
        ['sudo', 'mkdir', '-p', '/sys/kernel/config/usb_gadget/g1/functions/ecm.usb0'],
        ['sudo', 'bash', '-c', 'echo "DE:AD:BE:EF:00:01" > /sys/kernel/config/usb_gadget/g1/functions/ecm.usb0/host_addr'],
        ['sudo', 'bash', '-c', 'echo "DE:AD:BE:EF:00:02" > /sys/kernel/config/usb_gadget/g1/functions/ecm.usb0/dev_addr']
    ]

    for command in commands:
        if not run_command(command):
            log_and_print(f"Failed to execute command: {' '.join(command)}")
            return

    if not run_command(["sudo", "ln", "-s", "/sys/kernel/config/usb_gadget/g1/functions/ecm.usb0", "/sys/kernel/config/usb_gadget/g1/configs/c.1/"]):
        log_and_print("Failed to create symbolic link for ECM network.")

def main():
    while True:
        log_and_print("\nNetwork Configuration Interface\n")
        log_and_print("1. List known networks")
        log_and_print("2. Connect to new network")
        log_and_print("3. Exit")

        choice = input("Select an option: ")
        if choice == '1':
            update_or_remove_network()
        elif choice == '2':
            configure_wifi()
        elif choice == '3':
            exit()
        else:
            log_and_print("Invalid option. Please select a valid option.")

if __name__ == "__main__":
    if not os.geteuid() == 0:
        log_and_print("This script must be run as root. Please use sudo.")
        exit()
    main()
