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
        restart_network(ssid)
    except PermissionError:
        print("Permission denied. Please run this script with sudo.")

def restart_network(ssid):
    print("\nRestarting network services...\n")
    try:
        subprocess.run(["sudo", "systemctl", "restart", "dhcpcd"], check=True)
        print("\nNetwork services restarted.\n")

        print("\nChecking wifi connection...")
        time.sleep(10)
        result = subprocess.run(["sudo", "iwgetid"], capture_output=True, text=True)
        if ssid in result.stdout:
            print(f"\nSuccessfully connected to {ssid}\n")
        else:
            print(f"\nFailed to connect to {ssid}. Please check your credentials or network settings.\n")
    except subprocess.CalledProcessError as e:
        print(f"Failed to restart network services: {e}")

    print("\nConfiguration complete. You may now close this terminal.\n")

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
