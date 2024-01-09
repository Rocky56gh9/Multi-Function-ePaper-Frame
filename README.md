# multimode-epaper-frame
A DIY project resulting in an e-paper display built into a picture frame that uses an API from Reddit to pull and display Dad Jokes and Shower Thoughts, an API from OpenWeather to display a weather station, and web scraping to display a daily horoscope. Also includes a sleep image for the display for overnight hours.

# Equipment List

# New Build Guide
1. 
Install OS, enable SSH
Sudo apt-get update
Sudo apt-get upgrade
Sudo apt-get install libjpeg-dev
sudo apt-get install libopenjp2-7
sudo apt-get install python3-pip
pip install Pillow
Pip install pytz
Pip install bs4
sudo apt-get install git
git config --global http.postBuffer 524288000
pip3 install praw
sudo pip3 install RPi.GPIO
sudo pip3 install spidev
git clone https://github.com/waveshare/e-Paper.git
Sudo raspi-config
Enable SPI interface
Reboot
cd e-Paper/RaspberryPi_JetsonNano/
python [test script]
nano [real script]
Code:

# Handy Commands
1. Copy images from local machine to RaspberryPi:
scp /[path to script]/[image name].bmp [piusername]@[piip]:/[path to where you are housing scripts]

2. Clear SSH key from local machine:
ssh-keygen -R {RPi-IP-Address}

# Set Up Crontab Jobs
From the terminal, enter the command **crontab -e**, then, at the bottom of the file, enter each of these as an individual line.

1. 0 7-21 * * * /usr/bin/python3 /[path to script]/showerthoughts.py
2. 15 7-21 * * * /usr/bin/python3 /[path to script]/weatherstation.py
3. 30 7-21 * * * /usr/bin/python3 /[path to script]/dadjokes.py
4. 45 7-21 * * * /usr/bin/python3 /[path to script]/horoscope.py
5.  0 22 * * * /usr/bin/python3 /[path to script]/sleep.py
