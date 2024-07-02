#!/bin/bash

# Retry function with exponential backoff
retry() {
  local n=1
  local max=5
  local delay=5
  while true; do
    log "Executing command: $*"
    "$@" && break || {
      if [[ $n -lt $max ]]; then
        ((n++))
        log "Command failed. Attempt $n/$max."
        sleep $delay
        delay=$((delay * 2))
      else
        log "The command has failed after $n attempts."
        return 1
      fi
    }
  done
}

# Check network connectivity
check_network() {
  wget -q --spider http://google.com
  if [ $? -eq 0 ]; then
    log "Network is up."
  else
    log "Network is down. Check your internet connection."
    exit 1
  fi
}

# Manual package installation
manual_install_package() {
  local package_name="$1"
  local package_url="$2"
  log "Manually downloading and installing $package_name..."
  wget $package_url -O ${package_name}.tar.gz
  tar -xzf ${package_name}.tar.gz
  python3 -m pip install --no-cache-dir ${package_name}*
  check_package_installation "$package_name"
}

# Package installation with retry and fallback
install_package() {
  local package_name="$1"
  local pip_command="$2"
  local manual_url="$3"
  log "Attempting to install $package_name..."
  if ! retry $pip_command; then
    log "$package_name installation failed via pip. Attempting manual installation..."
    manual_install_package "$package_name" "$manual_url"
  fi
  check_package_installation "$package_name"
}

# Clone the repository with retries and fallbacks
clone_repo() {
  local repo_url="$1"
  local repo_dir="$2"
  log "Cloning repository: $repo_url into $repo_dir"
  if [ -d "$repo_dir" ]; then
    log "Directory '$repo_dir' already exists. Skipping clone."
    return 0
  fi

  if retry git clone $repo_url $repo_dir; then
    return 0
  else
    log "Failed to clone the repository."
    exit 1
  fi
}

# Verify package installation
check_package_installation() {
  local package_name="$1"
  python3 -c "import $package_name" &>/dev/null
  if [ $? -eq 0 ]; then
    log "$package_name is installed successfully."
  else
    log "$package_name is not installed. Retrying installation..."
    return 1
  fi
}

# Initialize script
log "Starting installation script..."
check_network

# Command execution with retry logic
retry sudo apt-get update --fix-missing &&
retry sudo apt-get install -y git python3-pip libjpeg-dev libopenjp2-7 libopenblas-base libopenblas-dev

# Add the user local bin to PATH to ensure scripts installed via pip are accessible
PATH="$HOME/.local/bin:$PATH"

# Package installations with verification
packages_to_install=(
  "Pillow https://files.pythonhosted.org/packages/58/b7/ece20939f84f3a4f9d6b344df82d30e0ed4b35a5e58e9a4b7b15c7870c2b/Pillow-8.1.2.tar.gz"
  "pytz https://files.pythonhosted.org/packages/41/aa/0b509ee60282b11d6a09c218beeb24c8f2281a2e8d7b708d9d44bb2dfdeb/pytz-2024.1.tar.gz"
  "bs4 https://files.pythonhosted.org/packages/91/f7/5e1a6e20b7edc17219f3fd1c10fc8c1708a80c867b09f2e2f5aaf8d03b65/beautifulsoup4-4.12.3.tar.gz"
  "praw https://files.pythonhosted.org/packages/2d/49/1f8ea5e875cf1a31c4b9d4f0e293c1e2c64c98a0f85ed19fd0f0c4f4ff8e/praw-7.7.1.tar.gz"
  "crontab https://files.pythonhosted.org/packages/fb/35/5a63ea0ed7c91f2a0c71e62a7f85edff6ef0efb99f8954781a3429cbfb69/python-crontab-2.5.1.tar.gz"
  "RPi.GPIO https://files.pythonhosted.org/packages/fd/57/3a2a4b1dc42b55c01e2b82ddda12e3b0e7ecb9ffb9f1c54e4785e89a6f6b/RPi.GPIO-0.7.1.tar.gz"
  "spidev https://files.pythonhosted.org/packages/6b/2e/60a5e29b8e1cb8d7e6b8cfc8a1251156a2b8f5b8c6cbe5cbdf979117f143/spidev-3.5.tar.gz"
  "timezonefinder https://files.pythonhosted.org/packages/2b/f7/10e278b8ef145da2e7f1480d7180b296ec53535985dc3bc5844f7191d9a0/timezonefinder-6.5.0.tar.gz"
)

for pkg_info in "${packages_to_install[@]}"; do
  pkg_name=$(echo $pkg_info | cut -d ' ' -f 1)
  pkg_url=$(echo $pkg_info | cut -d ' ' -f 2)
  install_package $pkg_name "python3 -m pip install --no-cache-dir $pkg_name" $pkg_url
done

# Cloning necessary repositories
echo "Cloning e-Paper repository..."
clone_repo "https://github.com/waveshare/e-Paper.git" "e-Paper"

# Enable SPI interface
echo "Enabling SPI interface..."
retry sudo raspi-config nonint do_spi 0

# Attempt to install rpi-connect if available
if ! retry sudo apt-get install -y rpi-connect; then
  log "Unable to install rpi-connect. Please verify if it is necessary or available for your system."
fi

# Enable user lingering
loginctl enable-linger $USER

# Start the Raspberry Pi Connect service for the current user, if available
if systemctl --user enable rpi-connect; then
  systemctl --user start rpi-connect
else
  log "Failed to start rpi-connect service. Check installation and service status."
fi

# Move back to the multimode-epaper-frame directory, if it exists
if cd "$HOME/multimode-epaper-frame"; then
  # Make sure the configuration scripts are executable
  chmod +x config/*.py
else
  log "Failed to locate the multimode-epaper-frame directory. Check the cloning process."
fi

# Final checks and completion messages
log "Installation script completed. Check $LOG_FILE for details."

echo "Initial Setup Complete. Please run the configuration scripts by entering the following in the terminal:"
echo ""
echo "cd ~/multimode-epaper-frame && chmod +x run_all_configs.py && ./run_all_configs.py"
