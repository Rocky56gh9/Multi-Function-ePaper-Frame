#!/bin/bash

# Function to execute a command and retry if it fails
execute_command() {
  local cmd="$1"
  local retries=3
  local count=0
  local delay=10

  until eval "$cmd"; do
    exit_code=$?
    count=$((count + 1))
    if [ $count -lt $retries ]; then
      echo "Command failed with exit code $exit_code. Retrying in $delay seconds..."
      sleep $delay
      delay=$((delay * 2))  # Exponential backoff
    else
      echo "Command failed after $count attempts."
      return $exit_code
    fi
  done
}

# Function to check network connectivity
check_network() {
  wget -q --spider http://google.com
  if [ $? -eq 0 ]; then
    echo "Network is up"
    return 0
  else
    echo "Network is down"
    return 1
  fi
}

# Function to manually download and install a Python package
manual_install_package() {
  local package_name="$1"
  local package_url="$2"

  echo "Manually downloading and installing $package_name..."
  wget $package_url -O ${package_name}.tar.gz
  tar -xzf ${package_name}.tar.gz
  pip3 install --no-cache-dir ${package_name}*
}

# Function to clone a repository with retries and local backup fallback
clone_repo() {
  local repo_url="$1"
  local repo_dir="$2"
  local backup_dir="$3"

  if [ -d "$repo_dir" ]; then
    echo "Directory '$repo_dir' already exists. Skipping clone."
    return 0
  fi

  if [ -d "$backup_dir" ]; then
    echo "Local backup found for '$repo_dir'. Copying from backup..."
    cp -r "$backup_dir" "$repo_dir"
    return 0
  fi

  echo "Cloning repository '$repo_url'..."
  execute_command "git clone $repo_url $repo_dir"
}

# Ensure that local bin is in PATH
export PATH=$PATH:$HOME/.local/bin

# Logging setup
log_file="setup.log"
exec > >(tee -i $log_file)
exec 2>&1

# Update and upgrade the system
echo "Updating and upgrading the system..."
execute_command "sudo apt-get update --fix-missing && sudo apt-get upgrade -y --fix-missing"

# Install necessary packages
echo "Installing necessary packages..."
execute_command "sudo apt-get install -y libjpeg-dev libopenjp2-7 python3-pip git"

# Install Python packages
echo "Installing Python packages..."
execute_command "pip3 install --no-cache-dir Pillow pytz bs4 praw crontab"
execute_command "sudo pip3 install --no-cache-dir RPi.GPIO spidev"

# Check network and fallback to manual installation if needed
if ! check_network; then
  echo "Network check failed. Attempting manual installation of timezonefinder..."
  manual_install_package "timezonefinder" "https://files.pythonhosted.org/packages/2b/f7/10e278b8ef145da2e7f1480d7180b296ec53535985dc3bc5844f7191d9a0/timezonefinder-6.5.0.tar.gz"
else
  echo "Installing timezonefinder package..."
  if ! execute_command "pip3 install --timeout 60 --no-cache-dir timezonefinder"; then
    manual_install_package "timezonefinder" "https://files.pythonhosted.org/packages/2b/f7/10e278b8ef145da2e7f1480d7180b296ec53535985dc3bc5844f7191d9a0/timezonefinder-6.5.0.tar.gz"
  fi
fi

# Clone the multimode-epaper-frame repository if it does not exist
echo "Cloning multimode-epaper-frame repository..."
clone_repo "https://github.com/Rocky56gh9/multimode-epaper-frame.git" "multimode-epaper-frame" "$HOME/multimode-epaper-frame-backup"

# Clone the e-Paper repository if it does not exist
echo "Cloning e-Paper repository..."
clone_repo "https://github.com/waveshare/e-Paper.git" "e-Paper" "$HOME/e-Paper-backup"

# Enable SPI interface
echo "Enabling SPI interface..."
execute_command "sudo raspi-config nonint do_spi 0"

# Configure USB access
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

# Make Python scripts executable
echo "Making Python scripts executable..."
chmod +x scripts/*.py

# Run configuration scripts
echo "Running configuration scripts..."
execute_command "python3 config/dadjokes_showerthoughts_config.py"
execute_command "python3 config/weatherstation_config.py"
execute_command "python3 config/crontab_config.py"

echo "Setup complete. Please reboot your system to apply all changes."

