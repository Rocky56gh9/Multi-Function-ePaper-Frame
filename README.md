# multimode-epaper-frame
A DIY project resulting in an e-paper display built into a picture frame that uses an API from Reddit to pull and display Shower Thoughts and Dad Jokes, an API from OpenWeather to display a weather station, and web scraping (from USA Today) to display a daily horoscope. Also includes a sleep image for the display for overnight hours. This can likley be adapted to other screens, but you'll need to work out the code changes. My build used a Raspberry Pi Zero WH and Waveshare 7.5"(B) tri-color e-paper display.

This project was my first attempt at any kind of python coding project. I saw a YouTube video about someone building a unit to display Shower Thoughts from Reddit, so I decided to take the plunge and try to create it myself. I really struggled to follow the instructions from that video series, and the equipment from the project would not even work with my setup for whatever reason. After initially giving up, I decided to try again and by chance, chose a larger screen which ended up working. The project is entirely self-taught using ChatGPT 4 (premium subscription). It took about 5 weeks and lots of trial and error but I eventually got it to work. As I got more comfortable, I continued to iterate, eventually adding all of the additional functionality shown here. I recognize that the code is not elegant, and the same variables/functionality differ between the different scripts, but they all function. I may in the future get around to trying to make the code more elegant and consistent, but in case anyone wants to try this build, hopefully this works for you!

# Equipment List
1. Option 1: [Raspberry Pi Zero WH](https://amzn.to/4aOmxIN) - This is an older version of the RPi, but the headers are already installed, so it's good to go out of the box. Slower than the Zero 2 W (below) but perfectly fine for this project.
2. Option 2: [Raspberry Pi Zero 2 W](https://amzn.to/3SdooQ2), [GPIO Pins (x2) and Installation Module](https://amzn.to/3vwNxfP) - For later versions of the project, I am using a Raspberry Pi Zero 2 W, which is notably faster, but the headers are sold separately and you need to install them manually. I found it to be quite easy to do so.
3. [Extra 40-Pin GPIO Solderless Header](https://amzn.to/3tFY4Vs)
4. [64 GB MicroSD Card](https://amzn.to/3Sc6vku)
5. [A/C Power adapter for MicroUSB](https://amzn.to/3TW36aX) OR [USB-A to MicroUSB](https://amzn.to/3NXCYbV) for powering from computer
6. [Waveshare 7.5" Tri-Color e-Paper Display with HAT Module](https://amzn.to/48PiB8I)
7. (Optional) [MicroUSB to Ethernet adapter](https://amzn.to/3RURdPJ) - Only needed if you will not be setting up wireless. This dongle is plug-and-play.
8. [Adafruit RaspberryPi Zero case](https://amzn.to/48sagbr)
9. [5x7 Matted Desktop Picture Frame](https://amzn.to/3tJUklN) for housing the screen for display

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

**Test the Screen**
Once you've done all of this, you're ready to see if everything is installed correctly. Run the test script for the specific screen.<br>
1. From the home prompt, enter **cd e-Paper/RaspberryPi_JetsonNano/python/examples**<br>
2. Run **python epd_7in5b_test.py**<br>

If the script runs and you see the series of test images run, you should be good to proceed!

# Copy Assets to Pi
1. Copy images from local machine to RaspberryPi:<br>
scp /[path to script]/[image name].bmp [piusername]@[piip]:/[path to where you are housing scripts] - Do this for each of the .bmp images.

In my case, I just left everything in the "examples" folder along with the test scripts. If I had it to do over again, I might put them elsewhere. But for now, I put the python scripts and images all in the same examples folder.

# Set Up Scripts
1. In the same examples folder, create each of the python files for the project.
2. Customize all of the variables to your preference, e.g., image locations, geographic location for weather, etc.
3. Run the scripts individually to test them out.

The Weather Station is hard-coded for Eastern time, but that should be adjustable, though those instructions are not included here.

# Set Up Crontab Jobs
Once you are happy with how the scripts run on the screen, from the terminal, enter the command **crontab -e**, then, at the bottom of the file, enter each of these as an individual line.

1. 0 7-21 * * * /usr/bin/python3 /[path to script]/showerthoughts.py
2. 15 7-21 * * * /usr/bin/python3 /[path to script]/weatherstation.py
3. 30 7-21 * * * /usr/bin/python3 /[path to script]/dadjokes.py
4. 45 7-21 * * * /usr/bin/python3 /[path to script]/horoscope.py
5.  0 22 * * * /usr/bin/python3 /[path to script]/sleep.py

# Physical Assembly

