# multimode-epaper-frame
A DIY project resulting in an e-paper display built into a picture frame that uses an API from Reddit to pull and display Dad Jokes and Shower Thoughts, an API from OpenWeather to display a weather station, and web scraping to display a daily horoscope. Also includes a sleep image for the display for overnight hours.

# Equipment List

# New Build Guide
1. Configure your SD card for the RaspberryPi. I used the Raspberry Pi installer on MacOS. Through that UI, give your unit a name (which is how it will appear on your network), then assign an ID and unique password. For ease of use later, also add your network SSID and password. On the second tab, be sure to enable enable SSH.
2. After the installer completes, put the SD card in the Pi and power it up. Depending on the unit, it could take ~10 minutes to appear on your network.
3. Log in to your router, find the unit name you assigned, and take note of the IP address.
4. Open a Terminal, and enter the command **SSH [unit name]@[ip address]**, followed by the password. Follow any additional prompts. **NOTE**, if you later scrap the build and start over, you likely need to reset the SSH key on your local device. Use the following command to clear it: **ssh-keygen -R {RPi-IP-Address}**
•	sudo apt-get update<br>
•	sudo apt-get upgrade<br>
•	sudo apt-get install libjpeg-dev<br>
•	sudo apt-get install libopenjp2-7
•	sudo apt-get install python3-pip
•	pip install Pillow
•	pip install pytz
•	pip install bs4
•	sudo apt-get install git
•	git config --global http.postBuffer 524288000
•	pip3 install praw
•	sudo pip3 install RPi.GPIO
•	sudo pip3 install spidev
•	git clone https://github.com/waveshare/e-Paper.git
•	sudo raspi-config
•	Enable SPI interface
•	Reboot
•	cd e-Paper/RaspberryPi_JetsonNano/
•	python [test script]

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
