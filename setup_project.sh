#!/bin/bash

# Variables for retry logic
max_attempts=5
initial_delay=5

# Function to retry a command with exponential backoff
retry() {
  local n=1
  local command="$@"
  until [ $n -ge $max_attempts ]; do
    eval "$command" && break
    echo "Command failed. Attempt $n/$max_attempts:"
    n=$((n + 1))
    sleep $((initial_delay ** n))
  done
  if [ $n -ge $max_attempts ]; then
    echo "The command has failed after $n attempts."
    return 1
  fi
}

# Function to ensure all required packages are installed
install_packages() {
  local packages=("$@")
  for package in "${packages[@]}"; do
    retry sudo apt-get install -y "$package" || return 1
  done
}

# Preserve the original user's home directory
ORIGINAL_HOME=$(eval echo ~${SUDO_USER})
project_dir="$ORIGINAL_HOME/multimode-epaper-frame"

# Check network connection
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

# Function to clone the repository
clone_repo() {
  local repo_url="$1"
  local dest_dir="$2"
  git clone "$repo_url" "$dest_dir" || return 1
}

# Function to check if a package is installed
is_installed() {
  dpkg -l | grep -qw "$1"
}

# Ensure the local bin is in PATH
export PATH=$PATH:$HOME/.local/bin

# Check network
if ! check_network; then
  exit 1
fi

# Update system packages
echo "Updating system packages..."
retry sudo apt-get update --fix-missing

# Install essential packages
essential_packages=(git git-lfs libjpeg-dev libopenjp2-7 python3-pip wget unzip)
install_packages "${essential_packages[@]}" || exit 1

# Configure git
git config --global http.postBuffer 524288000
git lfs install

# Clone the multimode-epaper-frame repository
if [ ! -d "$project_dir" ]; then
  echo "Cloning the repository..."
  retry clone_repo "https://github.com/Rocky56gh9/multimode-epaper-frame.git" "$project_dir" || {
    echo "Failed to clone the repository. Exiting."
    exit 1
  }
fi

# Move to the cloned directory
cd "$project_dir" || exit

# Install Python packages
python_packages=(
  "Pillow"
  "pytz"
  "beautifulsoup4"
  "praw"
  "python-crontab"
  "RPi.GPIO"
  "spidev"
  "timezonefinder"
)

for pkg in "${python_packages[@]}"; do
  retry pip3 install --timeout 60 --no-cache-dir "$pkg" || {
    echo "Failed to install $pkg. Exiting."
    exit 1
  }
done

# Clone the e-Paper repository
clone_repo "https://github.com/waveshare/e-Paper.git" "$project_dir/e-Paper" || {
  echo "Failed to clone the e-Paper repository. Exiting."
  exit 1
}

# Run configuration scripts as the original user
run_as_user() {
  sudo -u "$SUDO_USER" -H bash -c "$1"
}

run_as_user "python3 $project_dir/config/dadjokes_showerthoughts_config.py"
run_as_user "python3 $project_dir/config/weatherstation_config.py"
run_as_user "python3 $project_dir/config/crontab_config.py"

echo "Setup complete. Please reboot your system to apply all changes."
