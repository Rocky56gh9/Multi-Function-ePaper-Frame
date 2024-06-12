import os
import subprocess
import time

def configure_wifi():
    print("\nWiFi Configuration\n")
    add_wifi_settings()

def add_wifi_settings():
    ssid = input("\nEnter your WiFi SSID: ")
    psk = input("Enter your WiFi password: ")
    wifi_conf_path = '/etc/wpa_supplicant/wpa_supplicant.conf'
    backup_wifi_conf_path = '/etc/wpa_supplicant/wpa_supplicant.conf.bak'

    # Create a backup of the current WiFi configuration
    subprocess.run(["sudo", "cp", wifi_conf_path, backup_wifi_conf_path], check=True)

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
        print("\nNew WiFi settings added.\n")
        attempt_wifi_connection(ssid, backup_wifi_conf_path)
    except PermissionError:
        print("Permission denied. Please run this script with sudo.")

def attempt_wifi_connection(ssid, backup_wifi_conf_path):
    print("\nRestarting network services...\n")
    try:
        # Restart network services and preserve gadget mode
        preserve_gadget_mode()
        subprocess.run(["sudo", "systemctl", "restart", "dhcpcd"], check=True)
        print("\nNetwork services restarted.\n")

        print("\nTesting connection to the new WiFi network. This will take up to 30 seconds...")
        time.sleep(30)
        result = subprocess.run(["sudo", "iwgetid"], capture_output=True, text=True)
        if ssid in result.stdout:
            print(f"\nSuccessfully connected to {ssid}\n")
        else:
            print(f"\nFailed to connect to {ssid}. Reverting to previous WiFi settings...\n")
            revert_to_backup(backup_wifi_conf_path)
    except subprocess.CalledProcessError as e:
        print(f"Failed to restart network services: {e}")
        print("Reverting to previous WiFi settings...\n")
        revert_to_backup(backup_wifi_conf_path)

    print("\nConfiguration complete. You may now close this terminal.\n")

def revert_to_backup(backup_wifi_conf_path):
    wifi_conf_path = '/etc/wpa_supplicant/wpa_supplicant.conf'
    try:
        subprocess.run(["sudo", "cp", backup_wifi_conf_path, wifi_conf_path], check=True)
        preserve_gadget_mode()
        subprocess.run(["sudo", "systemctl", "restart", "dhcpcd"], check=True)
        print("\nReverted to previous WiFi settings and restarted network services.\n")
    except subprocess.CalledProcessError as e:
        print(f"Failed to revert to backup WiFi settings: {e}")
        print("\nManual intervention is required to restore WiFi settings. Please check your device configuration.\n")
        exit(1)

def preserve_gadget_mode():
    try:
        print("\nPreserving gadget mode settings...\n")
        subprocess.run(["sudo", "modprobe", "libcomposite"], check=True)
        subprocess.run(["sudo", "mkdir", "-p", "/sys/kernel/config/usb_gadget/g1"], check=True)
        subprocess.run(["sudo", "bash", "-c", 'echo 0x1d6b > /sys/kernel/config/usb_gadget/g1/idVendor'], check=True)
        subprocess.run(["sudo", "bash", "-c", 'echo 0x0104 > /sys/kernel/config/usb_gadget/g1/idProduct'], check=True)
        subprocess.run(["sudo", "bash", "-c", 'echo 0x0100 > /sys/kernel/config/usb_gadget/g1/bcdDevice'], check=True)
        subprocess.run(["sudo", "bash", "-c", 'echo 0x0200 > /sys/kernel/config/usb_gadget/g1/bcdUSB'], check=True)

        subprocess.run(["sudo", "mkdir", "-p", "/sys/kernel/config/usb_gadget/g1/strings/0x409"], check=True)
        subprocess.run(["sudo", "bash", "-c", 'echo "fedcba9876543210" > /sys/kernel/config/usb_gadget/g1/strings/0x409/serialnumber'], check=True)
        subprocess.run(["sudo", "bash", "-c", 'echo "Manufacturer" > /sys/kernel/config/usb_gadget/g1/strings/0x409/manufacturer'], check=True)
        subprocess.run(["sudo", "bash", "-c", 'echo "Product" > /sys/kernel/config/usb_gadget/g1/strings/0x409/product'], check=True)

        subprocess.run(["sudo", "mkdir", "-p", "/sys/kernel/config/usb_gadget/g1/configs/c.1/strings/0x409"], check=True)
        subprocess.run(["sudo", "bash", "-c", 'echo "Config 1: ECM network" > /sys/kernel/config/usb_gadget/g1/configs/c.1/strings/0x409/configuration'], check=True)
        subprocess.run(["sudo", "bash", '-c', 'echo 250 > /sys/kernel/config/usb_gadget/g1/configs/c.1/MaxPower'], check=True)

        subprocess.run(["sudo", "mkdir", "-p", "/sys/kernel/config/usb_gadget/g1/functions/ecm.usb0"], check=True)
        subprocess.run(["sudo", "bash", "-c", 'echo "DE:AD:BE:EF:00:01" > /sys/kernel/config/usb_gadget/g1/functions/ecm.usb0/host_addr'], check=True)
        subprocess.run(["sudo", "bash", "-c", 'echo "DE:AD:BE:EF:00:02" > /sys/kernel/config/usb_gadget/g1/functions/ecm.usb0/dev_addr'], check=True)

        if not os.path.exists("/sys/kernel/config/usb_gadget/g1/configs/c.1/ecm.usb0"):
            subprocess.run(["sudo", "ln", "-s", "/sys/kernel/config/usb_gadget/g1/functions/ecm.usb0", "/sys/kernel/config/usb_gadget/g1/configs/c.1/"], check=True)
        else:
            print("Symbolic link 'configs/c.1/ecm.usb0' already exists. Skipping link creation.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to preserve gadget mode settings: {e}")

def main():
    print("\nNetwork Configuration Interface\n")
    print("1. Add New WiFi Settings")
    print("2. Exit")
    
    choice = input("Select an option: ")
    if choice == '1':
        configure_wifi()
    elif choice == '2':
        exit()
    else:
        print("Invalid option. Please select a valid option.")
        main()

if __name__ == "__main__":
    if not os.geteuid() == 0:
        print("This script must be run as root. Please use sudo.")
        exit()
    main()
