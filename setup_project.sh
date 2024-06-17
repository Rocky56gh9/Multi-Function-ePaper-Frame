#!/bin/bash

# Retry function to execute a command and retry if it fails, with exponential backoff
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

# Function to manually download and install a Python package
manual_install_package() {
  local package_name="$1"
  local package_url="$2"

  echo "Manually downloading and installing $package_name..."
  wget $package_url -O ${package_name}.tar.gz
  tar -xzf ${package_name}.tar.gz
  pip3 install --no-cache-dir ${package_name}*
}

# Function to install a package with retries and manual fallback
install_package() {
  local package_name="$1"
  local pip_command="$2"
  local manual_url="$3"

  echo "Attempting to install $package_name..."
  if ! retry $pip_command; then
    echo "$package_name installation failed via pip. Attempting manual installation..."
    if ! manual_install_package "$package_name" "$manual_url"; then
      echo "$package_name manual installation also failed."
      return 1
    fi
  fi
  return 0
}

# Function to clone the repository with retries and fallbacks
clone_repo() {
  local repo_url="$1"
  local repo_dir="$2"

  if [ -d "$repo_dir" ]; then
    echo "Directory '$repo_dir' already exists. Skipping clone."
    return 0
  fi

  # Attempt using HTTPS first
  if retry git clone $repo_url $repo_dir; then
    return 0
  fi

  # If HTTPS fails, try using SSH if the user has SSH access configured
  if [ -f "$HOME/.ssh/id_rsa" ]; then
    local ssh_url=${repo_url/https:\/\/github.com\//git@github.com:}
    echo "Trying to clone using SSH: $ssh_url"
    if retry git clone $ssh_url $repo_dir; then
      return 0
    fi
  fi

  # As a last resort, try downloading the repository as a ZIP file and extracting it
  local zip_url=${repo_url}/archive/main.zip
  echo "Trying to download and unzip: $zip_url"
  if retry wget $zip_url -O ${repo_dir}.zip; then
    unzip ${repo_dir}.zip
    mv ${repo_dir}-main $repo_dir
    return 0
  fi

  echo "Failed to clone the repository."
  return 1
}

# Ensure the local bin is in PATH
export PATH=$PATH:$HOME/.local/bin

# Execute commands with retry logic
retry sudo apt-get update --fix-missing && \
retry sudo apt-get install -y git && \
git config --global http.postBuffer 524288000 && \
retry sudo apt-get install -y git-lfs && \
git lfs install && \
clone_repo "https://github.com/Rocky56gh9/multimode-epaper-frame.git" "multimode-epaper-frame"

# Move to the cloned directory
cd multimode-epaper-frame || exit

# Install necessary packages
echo "Installing necessary packages..."
retry sudo apt-get install -y libjpeg-dev libopenjp2-7 python3-pip

# Install Python packages with fallback logic
failed_packages=()

install_package "Pillow" "pip3 install --no-cache-dir Pillow" "https://files.pythonhosted.org/packages/58/b7/ece20939f84f3a4f9d6b344df82d30e0ed4b35a5e58e9a4b7b15c7870c2b/Pillow-8.1.2.tar.gz" || failed_packages+=("Pillow")
install_package "pytz" "pip3 install --no-cache-dir pytz" "https://files.pythonhosted.org/packages/41/aa/0b509ee60282b11d6a09c218beeb24c8f2281a2e8d7b708d9d44bb2dfdeb/pytz-2024.1.tar.gz" || failed_packages+=("pytz")
install_package "bs4" "pip3 install --no-cache-dir bs4" "https://files.pythonhosted.org/packages/91/f7/5e1a6e20b7edc17219f3fd1c10fc8c1708a80c867b09f2e2f5aaf8d03b65/beautifulsoup4-4.12.3.tar.gz" || failed_packages+=("bs4")
install_package "praw" "pip3 install --no-cache-dir praw" "https://files.pythonhosted.org/packages/2d/49/1f8ea5e875cf1a31c4b9d4f0e293c1e2c64c98a0f85ed19fd0f0c4f4ff8e/praw-7.7.1.tar.gz" || failed_packages+=("praw")
install_package "crontab" "pip3 install --no-cache-dir crontab" "https://files.pythonhosted.org/packages/fb/35/5a63ea0ed7c91f2a0c71e62a7f85edff6ef0efb99f8954781a3429cbfb69/python-crontab-2.5.1.tar.gz" || failed_packages+=("crontab")
install_package "RPi.GPIO" "sudo pip3 install --no-cache-dir RPi.GPIO" "https://files.pythonhosted.org/packages/fd/57/3a2a4b1dc42b55c01e2b82ddda12e3b0e7ecb9ffb9f1c54e4785e89a6f6b/RPi.GPIO-0.7.1.tar.gz" || failed_packages+=("RPi.GPIO")
install_package "spidev" "sudo pip3 install --no-cache-dir spidev" "https://files.pythonhosted.org/packages/6b/2e/60a5e29b8e1cb8d7e6b8cfc8a1251156a2b8f5b8c6cbe5cbdf979117f143/spidev-3.5.tar.gz" || failed_packages+=("spidev")

# Attempt to install timezonefinder with different methods
echo "Attempting to install timezonefinder..."
retry pip3 install --timeout 120 --no-cache-dir timezonefinder || {
  echo "Installing timezonefinder from source..."
  if ! retry manual_install_package "timezonefinder" "https://files.pythonhosted.org/packages/2b/f7/10e278b8ef145da2e7f1480d7180b296ec53535985dc3bc5844f7191d9a0/timezonefinder-6.5.0.tar.gz"; then
    echo "timezonefinder installation failed. Trying alternative source..."
    if ! retry manual_install_package "timezonefinder" "https://pypi.python.org/packages/source/t/timezonefinder/timezonefinder-6.5.0.tar.gz"; then
      failed_packages+=("timezonefinder")
    fi
  fi
}

# Check if there are any failed packages
if [ ${#failed_packages[@]} -ne 0 ]; then
  echo "The following packages failed to install:"
  for pkg in "${failed_packages[@]}"; do
    echo "- $pkg"
  done
else
  echo "All packages installed successfully."
fi

# Clone the e-Paper repository with robust logic
echo "Cloning e-Paper repository..."
clone_repo "https://github.com/waveshare/e-Paper.git" "e-Paper"

# Enable SPI interface
echo "Enabling SPI interface..."
retry sudo raspi-config nonint do_spi 0

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

echo "Initial Setup Complete. Please run the configuration scripts manually."
