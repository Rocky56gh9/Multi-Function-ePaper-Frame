#!/bin/bash

LOGFILE="/var/log/setup_project.log"

log_and_print() {
    echo "$1"
    echo "$1" >> "$LOGFILE"
}

retry_command() {
    local n=1
    local max=5
    local delay=10

    while true; do
        "$@" && break || {
            if [[ $n -lt $max ]]; then
                ((n++))
                log_and_print "Command failed. Attempt $n/$max:"
                sleep $delay;
            else
                log_and_print "The command has failed after $n attempts."
                return 1
            fi
        }
    done
}

check_network() {
    log_and_print "Checking network connectivity..."
    if ping -q -c 1 -W 1 google.com >/dev/null; then
        log_and_print "Network is up"
        return 0
    else
        log_and_print "Network is down. Please check your connection."
        return 1
    fi
}

install_packages() {
    log_and_print "Updating system packages..."
    retry_command sudo apt-get update

    log_and_print "Installing git..."
    retry_command sudo apt-get install -y git

    log_and_print "Installing git-lfs..."
    retry_command sudo apt-get install -y git-lfs

    log_and_print "Installing libjpeg-dev..."
    retry_command sudo apt-get install -y libjpeg-dev

    log_and_print "Installing libopenjp2-7..."
    retry_command sudo apt-get install -y libopenjp2-7

    log_and_print "Installing python3-pip..."
    retry_command sudo apt-get install -y python3-pip
}

install_python_packages() {
    log_and_print "Installing Pillow..."
    retry_command sudo pip3 install Pillow

    log_and_print "Installing pytz..."
    retry_command sudo pip3 install pytz

    log_and_print "Installing beautifulsoup4..."
    retry_command sudo pip3 install beautifulsoup4

    log_and_print "Installing praw..."
    retry_command sudo pip3 install praw

    log_and_print "Installing python-crontab..."
    retry_command sudo pip3 install python-crontab

    log_and_print "Installing RPi.GPIO..."
    retry_command sudo pip3 install RPi.GPIO

    log_and_print "Installing spidev..."
    retry_command sudo pip3 install spidev

    log_and_print "Installing timezonefinder..."
    if ! retry_command sudo pip3 install timezonefinder; then
        log_and_print "timezonefinder installation failed via pip. Attempting manual installation..."
        if retry_command wget -O timezonefinder.tar.gz https://files.pythonhosted.org/packages/2b/f7/10e278b8ef145da2e7f1480d7180b296ec53535985dc3bc5844f7191d9a0/timezonefinder-6.5.0.tar.gz; then
            tar -xzf timezonefinder.tar.gz
            cd timezonefinder-6.5.0 || exit
            if ! retry_command sudo python3 setup.py install; then
                log_and_print "timezonefinder manual installation also failed."
            fi
            cd ..
        else
            log_and_print "Failed to manually download timezonefinder."
        fi
    fi
}

clone_repositories() {
    log_and_print "Cloning multimode-epaper-frame repository..."
    retry_command git clone https://github.com/Rocky56gh9/multimode-epaper-frame.git

    log_and_print "Cloning e-Paper repository..."
    if ! retry_command git clone https://github.com/waveshare/e-Paper.git; then
        log_and_print "Failed to clone the e-Paper repository. Trying to download and unzip..."
        if ! retry_command wget https://github.com/waveshare/e-Paper/archive/main.zip; then
            log_and_print "Failed to download e-Paper zip file."
            exit 1
        fi
        unzip main.zip
    fi
}

main() {
    log_and_print "Starting setup script..."

    if ! check_network; then
        exit 1
    fi

    install_packages
    install_python_packages
    clone_repositories

    log_and_print "Setup complete."
}

main "$@"
