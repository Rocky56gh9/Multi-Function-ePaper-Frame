#!/bin/bash

# Function to execute a command and retry if it fails
execute_command() {
  local cmd=$1
  local retries=5
  local count=0

  until $cmd; do
    exit_code=$?
    count=$((count + 1))
    if [ $count -lt $retries ]; then
      echo "Command failed with exit code $exit_code. Retrying in 5 seconds..."
      sleep 5
    else
      echo "Command failed after $count attempts."
      return $exit_code
    fi
  done
}

echo "Updating and upgrading the system..."
execute_command "sudo apt-get update --fix-missing"
execute_command "sudo apt-get upgrade -y"

echo "Installing necessary packages..."
execute_command "sudo apt-get install -y libjpeg-dev libopenjp2-7 python3-pip git"

echo "Installing Python packages..."
execute_command "pip3 install Pillow pytz bs4 praw"
execute_command "sudo pip3 install RPi.GPIO spidev"

echo "Cloning multimode-epaper-frame repository..."
# Increase the postBuffer to handle large files
execute_command "git config --global http.postBuffer 524288000"
execute_command "git clone https://github.com/Rocky56gh9/multimode-epaper-frame.git"

cd multimode-epaper-frame

echo "Configuring device for USB access..."
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

echo "Setup complete. Please reboot your system to apply all changes."
