import os
import subprocess
import time

WIFI_CONF_PATH = '/etc/wpa_supplicant/wpa_supplicant.conf'
TEMP_WIFI_CONF_PATH = '/tmp/temp_wpa_supplicant.conf'

def configure_wifi():
    print("\nWiFi Configuration")
    print("1. Clear Existing WiFi Settings")
    print("2. Add New WiFi Settings")
    choice = input("Select an option: ")
    if choice == '1':
        clear_wifi_settings()
    elif choice == '2':
        add_wifi_settings()
    else:
        print("Invalid option. Please select a valid option.")
        configure_wifi()

def clear_wifi_settings():
    print("\nClearing existing WiFi settings...")
    try:
        with open(WIFI_CONF_PATH, 'w') as file:
            file.write("")
        print("Existing WiFi settings cleared.")
    except PermissionError:
        print("Permission denied. Please run this script with sudo.")

def add_wifi_settings():
    ssid = input("\nEnter your WiFi SSID: ")
    psk = input("Enter your WiFi password: ")
    wifi_conf = f"""
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=US

network={{
    ssid="{ssid}"
    psk="{psk}"
}}
"""
    try:
        with open(TEMP_WIFI_CONF_PATH, 'w') as file:
            file.write(wifi_conf)
        print(f"Temporary WiFi configuration written to {TEMP_WIFI_CONF_PATH}.")
        
        os.rename(TEMP_WIFI_CONF_PATH, WIFI_CONF_PATH)
        print(f"WiFi configuration updated and applied from {TEMP_WIFI_CONF_PATH} to {WIFI_CONF_PATH}.")

        # Restart network services to apply new settings
        restart_network()

        # Check if the device is connected to the new WiFi network
        check_wifi_connection(ssid)
    except PermissionError:
        print("Permission denied. Please run this script with sudo.")
    except Exception as e:
        print(f"An error occurred: {e}")

def restart_network():
    print("\nRestarting network services...")
    try:
        subprocess.run(["sudo", "systemctl", "restart", "dhcpcd"], check=True)
        print("Network services restarted.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to restart network services: {e}")

def check_wifi_connection(ssid):
    print("\nChecking WiFi connection...")
    time.sleep(10)  # Give some time for the network to restart and connect
    try:
        result = subprocess.run(["iwgetid"], capture_output=True, text=True)
        if ssid in result.stdout:
            print(f"Successfully connected to {ssid}")
        else:
            print(f"Failed to connect to {ssid}. Please check your credentials or network settings.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to check WiFi connection: {e}")

def main():
    print("\nWiFi Configuration Interface")
    print("1. Configure WiFi")
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
