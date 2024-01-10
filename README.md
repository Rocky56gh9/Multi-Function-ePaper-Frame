# multimode-epaper-frame
A DIY project resulting in an e-paper display built into a picture frame that uses an API from Reddit to pull and display Shower Thoughts and Dad Jokes, an API from OpenWeather to display a weather station, and web scraping (from USA Today) to display a daily horoscope. Also includes a sleep image for the display for overnight hours. This can likley be adapted to other screens, but you'll need to work out the code changes. My build used a Raspberry Pi Zero WH and Waveshare 7.5"(B) tri-color e-paper display.

This project was my first attempt at any kind of python coding project. I saw a YouTube video about someone building a unit to display Shower Thoughts from Reddit, so I decided to take the plunge and try to create it myself. I really struggled to follow the instructions from that video series, and the equipment from the project would not even work with my setup for whatever reason. After initially giving up, I decided to try again and by chance, chose a larger screen which ended up working. The project is entirely self-taught using ChatGPT 4 (premium subscription). It took about 5 weeks and lots of trial and error but I eventually got it to work. As I got more comfortable, I continued to iterate, eventually adding all of the additional functionality shown here. I recognize that the code is not elegant, and the same variables/functionality differ between the different scripts, but they all function. I may in the future get around to trying to make the code more elegant and consistent, but in case anyone wants to try this build, hopefully this works for you!

# Equipment List
1. Raspberry Pi Zero WH (for later copies of the project, I am using a Raspberry Pi Zero 2 W, but the headers are sold separately and you need to install them manually).
2. [Waveshare 7.5" Tri-Color e-Paper Display with HAT Module](https://amzn.to/48PiB8I)
3. 

# New Build Guide
1. Configure your SD card for the RaspberryPi. I used the Raspberry Pi installer on MacOS. Through that UI, give your unit a name (which is how it will appear on your network), then assign an ID and unique password. For ease of use later, also add your network SSID and password. On the second tab, be sure to enable enable SSH.
2. After the installer completes, put the SD card in the Pi and power it up. Depending on the unit, it could take ~10 minutes to appear on your network.
3. Log in to your router, find the unit name you assigned, and take note of the IP address.
4. Open a Terminal, and enter the command **SSH [unit name]@[ip address]**, followed by the password. Follow any additional prompts. **NOTE**, if you later scrap the build and start over, you likely need to reset the SSH key on your local device. Use the following command to clear it: **ssh-keygen -R {RPi-IP-Address}**<br>
•	sudo apt-get update<br>
•	sudo apt-get upgrade<br>
•	sudo apt-get install libjpeg-dev<br>
•	sudo apt-get install libopenjp2-7<br>
•	sudo apt-get install python3-pip<br>
•	pip install Pillow<br>
•	pip install pytz<br>
•	pip install bs4<br>
•	sudo apt-get install git<br>
•	git config --global http.postBuffer 524288000<br>
•	pip3 install praw<br>
•	sudo pip3 install RPi.GPIO<br>
•	sudo pip3 install spidev<br>
•	git clone https://github.com/waveshare/e-Paper.git<br>
•	sudo raspi-config<br>
•	Enable SPI interface<br>
•	Reboot<br>
•	cd e-Paper/RaspberryPi_JetsonNano/<br>
•	python [test script]<br>

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
