#!/bin/bash

# Install git
sudo apt-get update --fix-missing && \
sudo apt-get install -y git

# Clone the multimode-epaper-frame repository
git clone https://github.com/Rocky56gh9/multimode-epaper-frame.git

# Clone the e-Paper repository in the multimode-epaper-frame directory
cd multimode-epaper-frame || exit
git clone https://github.com/waveshare/e-Paper.git

# Move back to the root directory
cd ..

# Install necessary packages
sudo apt-get install -y libjpeg-dev libopenjp2-7 python3-pip

# Install Python packages
pip3 install --no-cache-dir Pillow pytz bs4 praw python-crontab RPi.GPIO spidev timezonefinder

# Enable USB gadget mode
echo "Enabling USB gadget mode..."
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

# Enable SPI interface
echo "Enabling SPI interface..."
sudo raspi-config nonint do_spi 0

echo "Initial Setup Complete. Please run the configuration scripts. Copy and paste the following into the terminal:"
echo "chmod +x multimode-epaper-frame/run_all_configs.py && ./multimode-epaper-frame/run_all_configs.py"
