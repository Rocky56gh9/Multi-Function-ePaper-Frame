#!/bin/bash

retry_command() {
    local n=1
    local max=2
    local delay=10
    while true; do
        "$@" && break || {
            if [[ $n -lt $max ]]; then
                ((n++))
                echo "Command failed. Attempt $n/$max:"
                sleep $delay;
            else
                echo "The command has failed after $n attempts."
                return 1
            fi
        }
    done
}

echo "Starting setup script for multimode-epaper-frame..."

# 3. Run sudo apt-get update
echo "Running sudo apt-get update..."
retry_command sudo apt-get update

# 4. Run sudo apt-get upgrade
echo "Running sudo apt-get upgrade..."
retry_command sudo apt-get upgrade -y

# 5. Install git
echo "Installing git..."
retry_command sudo apt-get install -y git

# 6. Configure git
echo "Configuring git..."
git config --global http.postBuffer 104857600  # Set buffer size to 100MB

# 7. Install git lfs
echo "Installing git lfs..."
retry_command sudo apt-get install -y git-lfs
git lfs install

# Enable git lfs
echo "Enabling git lfs..."
git lfs install

# 7a. Install pip
echo "Installing pip..."
retry_command sudo apt-get install -y python3-pip

# Function to clone repository using Git
clone_repo_git() {
    echo "Cloning the project repository using Git..."
    retry_command git clone https://github.com/Rocky56gh9/multimode-epaper-frame.git
}

# Function to download and unzip repository as a zip file
download_repo_zip() {
    echo "Downloading the project repository as a zip file..."
    retry_command wget https://github.com/Rocky56gh9/multimode-epaper-frame/archive/refs/heads/main.zip -O multimode-epaper-frame.zip
    echo "Unzipping the project repository..."
    retry_command unzip multimode-epaper-frame.zip
    mv multimode-epaper-frame-main multimode-epaper-frame
}

# Function to download repository using curl
download_repo_curl() {
    echo "Downloading the project repository using curl..."
    retry_command curl -L https://github.com/Rocky56gh9/multimode-epaper-frame/archive/refs/heads/main.zip -o multimode-epaper-frame.zip
    echo "Unzipping the project repository..."
    retry_command unzip multimode-epaper-frame.zip
    mv multimode-epaper-frame-main multimode-epaper-frame
}

# Attempt to clone the repository using Git, fallback to other methods if Git fails
clone_repo() {
    if clone_repo_git; then
        echo "Successfully cloned the repository using Git."
    elif download_repo_zip; then
        echo "Successfully downloaded and unzipped the repository using wget."
    elif download_repo_curl; then
        echo "Successfully downloaded and unzipped the repository using curl."
    else
        echo "Failed to clone the repository using all methods."
        exit 1
    fi
}

# Clone the project repository
clone_repo
cd multimode-epaper-frame || { echo "Failed to change directory to multimode-epaper-frame"; exit 1; }

# 9. Install Pillow
echo "Installing Pillow..."
retry_command pip3 install Pillow

# 10. Install pytz
echo "Installing pytz..."
retry_command pip3 install pytz

# 11. Install bs4
echo "Installing BeautifulSoup4..."
retry_command pip3 install bs4

# 12. Install praw
echo "Installing praw..."
retry_command pip3 install praw

# 13. Install crontab
echo "Installing crontab..."
retry_command sudo apt-get install -y cron

# 14. Install RPI.GPIO
echo "Installing RPI.GPIO..."
retry_command pip3 install RPi.GPIO

# 15. Install spidev
echo "Installing spidev..."
retry_command pip3 install spidev

# 16. Install timezonefinder
echo "Installing timezonefinder..."
retry_command pip3 install timezonefinder

# 17. Clone the e-Paper repository inside multimode-epaper-frame directory
echo "Cloning the e-Paper repository..."
cd multimode-epaper-frame || { echo "Failed to change directory to multimode-epaper-frame"; exit 1; }
retry_command git clone https://github.com/waveshare/e-Paper.git

# 18. Enable SPI interface
echo "Enabling SPI interface..."
sudo raspi-config nonint do_spi 0

# 19. Configure USB gadget mode
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

# 20. Move back to the home directory
echo "Moving back to the multimode-epaper-frame directory..."
cd ~/multimode-epaper-frame

# 21. Make the python scripts executable
echo "Making Python scripts executable..."
chmod +x *.py

# 22. Run each of the configuration scripts
echo "Running configuration scripts..."
for script in config/*.sh; do
  echo "Running $script..."
  bash "$script"
done

echo "Setup completed. Checking installation status..."

# Verify the installation
python3 -m unittest discover -s tests || { echo "Some tests failed"; exit 1; }

echo "All installations and configurations were successful."
