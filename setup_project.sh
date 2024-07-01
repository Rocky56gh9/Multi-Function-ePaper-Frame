#!/bin/bash

# Retry function with exponential backoff
retry() {
  local n=1
  local max=5
  local delay=5
  while true; do
    "$@" && break || {
      if [[ $n -lt $max ]]; then
        ((n++))
        echo "Command failed. Attempt $n/$max:"
        sleep $delay
        delay=$((delay * 2))  # Exponential backoff
      else
        echo "The command has failed after $n attempts."
        return 1
      fi
    }
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

# Function to install a package with retries
install_package() {
  local package_name="$1"
  local pip_command="$2"

  echo "Attempting to install $package_name..."
  retry $pip_command --break-system-packages
  if [ $? -ne 0 ]; then
    echo "$package_name installation failed."
    return 1
  fi
  return 0
}

# Function to clone the repository
clone_repo() {
  local repo_url="$1"
  local repo_dir="$2"

  if [ -d "$repo_dir" ]; then
    echo "Directory '$repo_dir' already exists. Skipping clone."
    return 0
  fi

  if retry git clone $repo_url $repo_dir; then
    return 0
  fi

  if [ -f "$HOME/.ssh/id_rsa" ]; then
    local ssh_url=${repo_url/https:\/\/github.com\//git@github.com:}
    echo "Trying to clone using SSH: $ssh_url"
    retry git clone $ssh_url $repo_dir
  else
    echo "SSH not configured. Cloning via HTTPS failed."
    return 1
  fi
}

# Ensure the local bin is in PATH
export PATH=$PATH:$HOME/.local/bin

# Check network connectivity
if ! check_network; then
  echo "Network check failed. Please ensure you are connected to the internet."
  exit 1
fi

# Execute commands with retry logic
retry sudo apt-get update --fix-missing
retry sudo apt-get install -y git libjpeg-dev libopenjp2-7 python3-pip git-lfs
git config --global http.postBuffer 524288000
git lfs install

clone_repo "https://github.com/Rocky56gh9/multimode-epaper-frame.git" "multimode-epaper-frame"

cd multimode-epaper-frame || exit

# Install necessary packages
echo "Installing necessary packages..."
required_packages=("Pillow" "pytz" "beautifulsoup4" "praw" "python-crontab" "RPi.GPIO" "spidev" "timezonefinder")
failed_packages=()

for pkg in "${required_packages[@]}"; do
  if ! install_package "$pkg" "pip3 install --no-cache-dir $pkg"; then
    failed_packages+=("$pkg")
  fi
done

if [ ${#failed_packages[@]} -ne 0 ]; then
  echo "The following packages failed to install:"
  for pkg in "${failed_packages[@]}"; do
    echo "- $pkg"
  done
else
  echo "All packages installed successfully."
fi

clone_repo "https://github.com/waveshare/e-Paper.git" "e-Paper"

echo "Enabling SPI interface..."
retry sudo raspi-config nonint do_spi 0

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

# Install Raspberry Pi Connect
echo "Installing Raspberry Pi Connect..."
retry sudo apt-get install -y rpi-connect

# Enable user lingering
loginctl enable-linger $USER

# Start the Raspberry Pi Connect service for the current user
echo "Starting the Raspberry Pi Connect service for the current user..."
systemctl --user enable rpi-connect
systemctl --user start rpi-connect

echo "Initial Setup Complete. Initiating configuration scripts..."
sleep 5

cd "$HOME/multimode-epaper-frame" || exit

chmod +x config/*.py

echo "Initial Setup Complete. Please run the configuration scripts by entering the following in the terminal:"
echo ""
echo "cd ~/multimode-epaper-frame && chmod +x run_all_configs.py && ./run_all_configs.py"
