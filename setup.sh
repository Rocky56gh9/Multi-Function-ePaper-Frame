#!/bin/bash

RETRY_LIMIT=5

function retry() {
    local n=1
    local max=$RETRY_LIMIT
    local delay=5
    local cmd="$@"

    while true; do
        echo "Attempt $n/$max: $cmd"
        $cmd && break || {
            if [[ $n -lt $max ]]; then
                ((n++))
                echo "Command failed. Retrying in $delay seconds..."
                sleep $delay
            else
                echo "The command has failed after $n attempts."
                return 1
            fi
        }
    done
}

# Update and upgrade the system
retry sudo apt-get update --fix-missing
retry sudo apt-get upgrade -y

# Install necessary packages with --fix-missing to handle missing packages
PACKAGES="libjpeg-dev libopenjp2-7 python3-pip git"
for package in $PACKAGES; do
    retry sudo apt-get install -y $package --fix-missing
done

# Install Python packages
PYTHON_PACKAGES="Pillow pytz bs4 praw requests timezonefinder RPi.GPIO spidev"
for package in $PYTHON_PACKAGES; do
    retry sudo pip3 install $package
done

# Clone the e-Paper library
if [ ! -d "e-Paper" ]; then
    retry git clone https://github.com/waveshare/e-Paper.git
else
    echo "e-Paper library already exists. Skipping clone."
fi

# Copy necessary images and scripts
retry cp -r e-Paper/RaspberryPi_JetsonNano/python/examples/7.5inch_e-paper_code/images/*.bmp images/
retry cp e-Paper/RaspberryPi_JetsonNano/python/examples/7.5inch_e-paper_code/*.py scripts/

# Configure device for USB access
echo "Configuring device for USB access..."
# Add your gadget mode setup code here if needed

echo "Setup complete. Please reboot your system to apply all changes."

# Summary
errors=0

function check_command() {
    if ! $1; then
        echo "Failed: $1"
        errors=$((errors + 1))
    fi
}

check_command "pip3 --version"
for package in $PYTHON_PACKAGES; do
    check_command "pip3 show $package"
done

if [[ $errors -gt 0 ]]; then
    echo "There were $errors errors during setup. Please re-run the setup script."
else
    echo "Setup completed successfully!"
fi
