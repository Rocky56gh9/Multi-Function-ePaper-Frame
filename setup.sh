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

# Ensure that local bin is in PATH
export PATH=$PATH:$HOME/.local/bin

# Logging setup
log_file="setup.log"
exec > >(tee -i $log_file)
exec 2>&1

echo "Updating and upgrading the system..."
execute_command "sudo apt-get update --fix-missing"
execute_command "sudo apt-get upgrade -y --fix-missing"

echo "Installing necessary packages..."
execute_command "sudo apt-get install -y libjpeg-dev libopenjp2-7 python3-pip git"

echo "Installing Python packages..."
execute_command "pip3 install --no-cache-dir Pillow pytz bs4 praw timezonefinder crontab"
execute_command "sudo pip3 install --no-cache-dir RPi.GPIO spidev"

echo "Cloning multimode-epaper-frame repository..."
# Increase the postBuffer to handle large files
execute_command "git config --global http.postBuffer 524288000"
if [ ! -d "multimode-epaper-frame" ]; then
  execute_command "git clone https://github.com/Rocky56gh9/multimode-epaper-frame.git"
else
  echo "Directory 'multimode-epaper-frame' already exists. Skipping clone."
fi

echo "Cloning e-Paper repository..."
if [ ! -d "e-Paper" ]; then
  execute_command "git clone https://github.com/waveshare/e-Paper.git"
else
  echo "Directory 'e-Paper' already exists. Skipping clone."
fi

cd multimode-epaper-frame || exit

echo "Configuring device for USB access..."
sudo modprobe libcomposite
sudo mkdir -p /sys/kernel/config/usb_gadget/g1
cd /sys/kernel/config/usb_gadget/g1 || exit
echo 0x1d6b | sudo tee idVendor # Linux Foundation
echo 0x0104 | sudo tee idProduct # Multifunction Composite Gadget
echo 0x0100 | sudo tee bcdDevice # v1.0.0
echo 0x0200 | sudo tee bcdUSB # USB2

sudo mkdir -p strings/0x409
echo "fedcba9876543210" | sudo tee strings/0x409/serialnumber
echo "Manufacturer" | sudo tee strings/0x409/manufacturer
echo "Product" | sudo tee strings/0x409/product

sudo mkdir -p configs/c.1/strings/0x409
echo "Config 1: ECM network" | sudo tee configs/c.1/strings/0x409/configuration
echo 250 | sudo tee configs/c.1/MaxPower

sudo mkdir -p functions/ecm.usb0
echo "DE:AD:BE:EF:00:01" | sudo tee functions/ecm.usb0/host_addr || echo "Skipping host_addr configuration as it is busy."
echo "DE:AD:BE:EF:00:02" | sudo tee functions/ecm.usb0/dev_addr || echo "Skipping dev_addr configuration as it is busy."

if [ ! -L configs/c.1/ecm.usb0 ]; then
  sudo ln -s functions/ecm.usb0 configs/c.1/
else
  echo "Symbolic link 'configs/c.1/ecm.usb0' already exists. Skipping link creation."
fi

cd "$HOME/multimode-epaper-frame" || exit

echo "Making Python scripts executable..."
chmod +x scripts/*.py

echo "Running configuration scripts..."
execute_command "python3 config/dadjokes_showerthoughts_config.py"
execute_command "python3 config/weatherstation_config.py"
execute_command "python3 config/crontab_config.py"

echo "Setup complete. Please reboot your system to apply all changes."
