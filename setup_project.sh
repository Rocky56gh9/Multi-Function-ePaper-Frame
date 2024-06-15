#!/bin/bash

echo "Starting setup script for multimode-epaper-frame..."

# 3. Run sudo apt-get update
echo "Running sudo apt-get update..."
sudo apt-get update

# 4. Run sudo apt-get upgrade
echo "Running sudo apt-get upgrade..."
sudo apt-get upgrade -y

# 5. Install git
echo "Installing git..."
sudo apt-get install -y git

# 6. Configure git
echo "Configuring git..."
git config --global http.postBuffer 524288000

# 7. Install git lfs
echo "Installing git lfs..."
sudo apt-get install -y git-lfs
git lfs install

# 7a. Install pip
echo "Installing pip..."
sudo apt-get install -y python3-pip

# 8. Clone the project repository
echo "Cloning the project repository..."
git clone https://github.com/Rocky56gh9/multimode-epaper-frame.git
cd multimode-epaper-frame || { echo "Failed to change directory to multimode-epaper-frame"; exit 1; }

# 9. Install Pillow
echo "Installing Pillow..."
pip3 install Pillow

# 10. Install pytz
echo "Installing pytz..."
pip3 install pytz

# 11. Install bs4
echo "Installing BeautifulSoup4..."
pip3 install bs4

# 12. Install praw
echo "Installing praw..."
pip3 install praw

# 13. Install crontab
echo "Installing crontab..."
sudo apt-get install -y cron

# 14. Install RPI.GPIO
echo "Installing RPI.GPIO..."
pip3 install RPi.GPIO

# 15. Install spidev
echo "Installing spidev..."
pip3 install spidev

# 16. Install timezonefinder
echo "Installing timezonefinder..."
pip3 install timezonefinder

# 17. Clone the e-Paper repository
echo "Cloning the e-Paper repository..."
git clone https://github.com/waveshare/e-Paper.git

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
