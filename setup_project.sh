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

# Check network connectivity
if ! check_network; then
  echo "Network check failed. Please ensure you are connected to the internet."
  exit 1
fi

# Execute commands with retry logic
retry sudo apt-get update --fix-missing && \
retry sudo apt-get install -y git libjpeg-dev libopenjp2-7 python3-pip git-lfs python3-bs4 python3-praw python3-rpi.gpio python3-spidev python3-pil python3-tz && \
git config --global http.postBuffer 524288000 && \
git lfs install && \
clone_repo "https://github.com/Rocky56gh9/multimode-epaper-frame.git" "multimode-epaper-frame"

# Move to the cloned directory
cd multimode-epaper-frame || exit

# Clone the e-Paper repository with robust logic
echo "Cloning e-Paper repository..."
clone_repo "https://github.com/waveshare/e-Paper.git" "e-Paper"

# Enable SPI interface
echo "Enabling SPI interface..."
retry sudo raspi-config nonint do_spi 0

# Install Raspberry Pi Connect
echo "Installing Raspberry Pi Connect..."
retry sudo apt-get install -y rpi-connect

# Enable user lingering
loginctl enable-linger $USER

# Start the Raspberry Pi Connect service for the current user
echo "Starting the Raspberry Pi Connect service for the current user..."
systemctl --user enable rpi-connect
systemctl --user start rpi-connect

# Move back to the multimode-epaper-frame directory
cd "$HOME/multimode-epaper-frame" || exit

# Make sure the configuration scripts are executable
chmod +x config/*.py

echo "Initial Setup Complete. Please run the configuration scripts by entering the following in the terminal:"
echo ""
echo "cd ~/multimode-epaper-frame && chmod +x run_all_configs.py && ./run_all_configs.py"
