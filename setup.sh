#!/bin/bash

# Update and upgrade the system
sudo apt-get update
sudo apt-get upgrade -y

# Install necessary packages
sudo apt-get install -y libjpeg-dev libopenjp2-7 python3-pip git

# Install Python packages
pip install Pillow pytz bs4 praw
sudo pip3 install RPi.GPIO spidev

# Clone the e-Paper repository
git clone https://github.com/waveshare/e-Paper.git

# Configure git
git config --global http.postBuffer 524288000

# Copy image files to appropriate location using dynamic home directory
mkdir -p $HOME/multimode-epaper-frame/images
cp *.bmp $HOME/multimode-epaper-frame/images/

# Copy Python scripts to appropriate location using dynamic home directory
mkdir -p $HOME/multimode-epaper-frame/scripts
cp *.py $HOME/multimode-epaper-frame/scripts/

# Enable SPI interface (This will open the raspi-config tool, requiring user interaction)
sudo raspi-config nonint do_spi 0

# Configure USB access
echo "Configuring device for USB access..."
sudo modprobe g_serial
sudo systemctl enable getty@ttyGS0.service
sudo systemctl start getty@ttyGS0.service

echo "USB access configured successfully."

# Create a flag file to indicate first boot
touch $HOME/multimode-epaper-frame/first_boot_flag

# Ensure first_boot.sh is executable
chmod +x $HOME/multimode-epaper-frame/scripts/first_boot.sh

# Add the first boot check to .bashrc automatically
if ! grep -q 'first_boot.sh' $HOME/.bashrc; then
    echo 'if [ -f $HOME/multimode-epaper-frame/first_boot_flag ]; then' >> $HOME/.bashrc
    echo '    $HOME/multimode-epaper-frame/scripts/first_boot.sh' >> $HOME/.bashrc
    echo 'fi' >> $HOME/.bashrc
fi

# Configure crontab for other scripts
(crontab -l 2>/dev/null; echo "0 7-21 * * * /usr/bin/python3 $HOME/multimode-epaper-frame/scripts/showerthoughts.py") | crontab -
(crontab -l 2>/dev/null; echo "15 7-21 * * * /usr/bin/python3 $HOME/multimode-epaper-frame/scripts/weatherstation.py") | crontab -
(crontab -l 2>/dev/null; echo "30 7-21 * * * /usr/bin/python3 $HOME/multimode-epaper-frame/scripts/dadjokes.py") | crontab -
(crontab -l 2>/dev/null; echo "45 7-21 * * * /usr/bin/python3 $HOME/multimode-epaper-frame/scripts/horoscope.py") | crontab -
(crontab -l 2>/dev/null; echo "0 22 * * * /usr/bin/python3 $HOME/multimode-epaper-frame/scripts/sleep.py") | crontab -

echo "Setup complete. Please reboot your system to apply all changes."
