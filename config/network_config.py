import os
import subprocess
import time
import logging

# Configure logging
logging.basicConfig(filename='/var/log/wifi_config.log', level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')

def log_and_print(message):
    print(message)
    logging.info(message)

def run_command(command, retries=3, delay=5):
    for attempt in range(retries):
        try:
            subprocess.run(command, check=True)
            return True
        except subprocess.CalledProcessError as e:
            log_and_print(f"Command failed: {e}. Retrying ({attempt + 1}/{retries})...")
            time.sleep(delay)
    return False

def configure_wifi():
    log_and_print("\nWiFi Configuration\n")
    add_wifi_settings()

def add_wifi_settings():
    while True:
        ssid = input("\nEnter your WiFi SSID: ").strip()
        psk = input("Enter your WiFi password: ").strip()
        if ssid and psk:
            break
        log_and_print("SSID and password cannot be empty. Please try again.")

    wifi_conf_path = '/etc/wpa_supplicant/wpa_supplicant.conf'
    backup_wifi_conf_path = '/etc/wpa_supplicant/wpa_supplicant.conf.bak'

    # Create a backup of the current WiFi configuration
    if not run_command(["sudo", "cp", wifi_conf_path, backup_wifi_conf_path]):
        log_and_print("Failed to create backup of WiFi configuration. Aborting.")
        exit(1)

    log_and_print("\nBackup of current WiFi configuration created.\n")

    # New WiFi settings
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

    attempt_wifi_connection(ssid, backup_wifi_conf_path)

def attempt_wifi_connection(ssid, backup_wifi_conf_path):
    log_and_print("\nRestarting network services...\n")
    if not run_command(["sudo", "systemctl", "restart", "dhcpcd"]):
        log_and_print("Failed to restart network services. Reverting to previous WiFi settings...")
        revert_to_backup(backup_wifi_conf_path)
        return

    log_and_print("\nNetwork services restarted.\n")
    log_and_print("\nTesting connection to the new WiFi network. This will take up to 30 seconds...")
    time.sleep(30)

    result = subprocess.run(["sudo", "iwgetid"], capture_output=True, text=True)
    if ssid in result.stdout:
        log_and_print(f"\nSuccessfully connected to {ssid}\n")
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
    if not run_command(["sudo", "systemctl", "restart", "dhcpcd"]):
        log_and_print("Failed to restart network services after reverting to backup. Manual intervention required.")
        exit(1)

    log_and_print("\nReverted to previous WiFi settings and restarted network services.\n")

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
    log_and_print("\nNetwork Configuration Interface\n")
    log_and_print("1. Add New WiFi Settings")
    log_and_print("2. Exit")
    
    choice = input("Select an option: ")
    if choice == '1':
        configure_wifi()
    elif choice == '2':
        exit()
    else:
        log_and_print("Invalid option. Please select a valid option.")
        main()

if __name__ == "__main__":
    if not os.geteuid() == 0:
        log_and_print("This script must be run as root. Please use sudo.")
        exit()
    main()
