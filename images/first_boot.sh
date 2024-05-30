#!/bin/bash

# Check if this is the first boot and if connected via SSH
if [ -f $HOME/multimode-epaper-frame/first_boot_flag ] && [ -n "$SSH_CONNECTION" ]; then
    # Check if WiFi credentials are already configured
    if ! grep -q 'network={' /etc/wpa_supplicant/wpa_supplicant.conf; then
        # Prompt user for WiFi SSID and password
        read -p "Please enter your WiFi SSID: " ssid
        read -sp "Please enter your WiFi password: " psk
        echo

        # Configure WiFi
        cat <<EOF | sudo tee -a /etc/wpa_supplicant/wpa_supplicant.conf
network={
    ssid="$ssid"
    psk="$psk"
}
EOF

        sudo systemctl restart dhcpcd
    fi

    # Remove the flag file
    rm $HOME/multimode-epaper-frame/first_boot_flag
fi
