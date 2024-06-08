#!/bin/bash

# Update and upgrade the system
sudo apt-get update
sudo apt-get upgrade -y

# Install necessary packages
sudo apt-get install -y libjpeg-dev libopenjp2-7 python3-pip git

# Install Python packages
pip3 install Pillow pytz bs4 praw requests timezonefinder RPi.GPIO spidev

# Clone the e-Paper repository
git clone https://github.com/waveshare/e-Paper.git

# Copy image files to appropriate location using dynamic home directory
mkdir -p $HOME/multimode-epaper-frame/images
cp *.bmp $HOME/multimode-epaper-frame/images/

# Copy Python scripts to appropriate location using dynamic home directory
mkdir -p $HOME/multimode-epaper-frame/scripts
cp *.py $HOME/multimode-epaper-frame/scripts/

# Enable SPI interface
sudo raspi-config nonint do_spi 0

# Configure USB access
echo "Configuring device for USB access..."
sudo modprobe g_serial
sudo systemctl enable getty@ttyGS0.service
sudo systemctl start getty@ttyGS0.service

echo "USB access configured successfully."

echo "Setup complete. Please reboot your system to apply all changes."
