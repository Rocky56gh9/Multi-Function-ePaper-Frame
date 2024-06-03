import os
import subprocess

def configure_gadget_mode():
    print("Gadget Mode Configuration")
    print("1. Turn Gadget Mode ON")
    print("2. Turn Gadget Mode OFF")
    choice = input("Select an option: ")
    if choice == '1':
        enable_gadget_mode()
    elif choice == '2':
        disable_gadget_mode()
    else:
        print("Invalid option. Please select a valid option.")
        configure_gadget_mode()

def enable_gadget_mode():
    print("Enabling Gadget Mode for local USB access...")
    gadget_mode_script = """
    sudo modprobe libcomposite
    cd /sys/kernel/config/usb_gadget/
    mkdir -p g1
    cd g1
    echo 0x1d6b > idVendor # Linux Foundation
    echo 0x0104 > idProduct # Multifunction Composite Gadget
    echo 0x0100 > bcdDevice # v1.0.0
    echo 0x0200 > bcdUSB # USB2
    mkdir -p strings/0x409
    echo "fedcba9876543210" > strings/0x409/serialnumber
    echo "Manufacturer" > strings/0x409/manufacturer
    echo "Product" > strings/0x409/product
    mkdir -p configs/c.1/strings/0x409
    echo "Config 1: ECM network" > configs/c.1/strings/0x409/configuration
    echo 250 > configs/c.1/MaxPower
    mkdir -p functions/ecm.usb0
    echo "DE:AD:BE:EF:00:01" > functions/ecm.usb0/host_addr
    echo "DE:AD:BE:EF:00:02" > functions/ecm.usb0/dev_addr
    ln -s functions/ecm.usb0 configs/c.1/
    """
    subprocess.run(gadget_mode_script, shell=True, check=True)
    print("Gadget mode enabled.")

def disable_gadget_mode():
    print("Disabling Gadget Mode for local USB access...")
    gadget_mode_script = """
    cd /sys/kernel/config/usb_gadget/g1
    rm configs/c.1/ecm.usb0
    rmdir configs/c.1/strings/0x409
    rmdir configs/c.1
    rmdir functions/ecm.usb0
    rmdir strings/0x409
    cd ..
    rmdir g1
    sudo modprobe -r libcomposite
    """
    subprocess.run(gadget_mode_script, shell=True, check=True)
    print("Gadget mode disabled.")

def configure_wifi():
    print("WiFi Configuration")
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
    print("Clearing existing WiFi settings...")
    wifi_conf_path = '/etc/wpa_supplicant/wpa_supplicant.conf'
    with open(wifi_conf_path, 'w') as file:
        file.write("")
    print("Existing WiFi settings cleared.")

def add_wifi_settings():
    ssid = input("Enter your WiFi SSID: ")
    psk = input("Enter your WiFi password: ")
    wifi_conf_path = '/etc/wpa_supplicant/wpa_supplicant.conf'
    wifi_conf = f"""
network={{
    ssid="{ssid}"
    psk="{psk}"
}}
"""
    with open(wifi_conf_path, 'a') as file:
        file.write(wifi_conf)
    print("New WiFi settings added.")
    subprocess.run(["sudo", "systemctl", "restart", "dhcpcd"], check=True)

def main():
    print("Network Configuration Interface")
    print("1. Configure Gadget Mode")
    print("2. Configure WiFi")
    print("3. Exit")
    
    choice = input("Select an option: ")
    if choice == '1':
        configure_gadget_mode()
    elif choice == '2':
        configure_wifi()
    elif choice == '3':
        exit()
    else:
        print("Invalid option. Please select a valid option.")
        main()

if __name__ == "__main__":
    main()
