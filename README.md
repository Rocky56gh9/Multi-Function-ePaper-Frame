# e-Paper Multi-Function Display
An e-paper multi-function display project using an API from Reddit to pull and display Shower Thoughts and Dad Jokes, an API from OpenWeather to display a weather station, and web scraping to display a daily horoscope. Also includes a sleep image for the display for overnight hours. This can likley be adapted to other screens, but you'll need to work out the code changes. My build used a Raspberry Pi Zero WH and Waveshare 7.5"(B) tri-color e-paper display.

This project was my first attempt at any kind of python coding and is entirely self-taught using ChatGPT-4. I recognize that the code is not elegant, and the same variables/functionality differ between the different scripts, but they all work. I may in the future get around to trying to make the code more elegant and consistent, but in case anyone wants to try this build, hopefully this works for you!

The overall cost for the project is about $150 USD.

![IMG_3032](https://github.com/Rocky56gh9/multimode-epaper-frame/assets/154940519/e9c3cef0-a6a2-4a1f-8abf-4e7857c67fc6)<br>
![IMG_3031](https://github.com/Rocky56gh9/multimode-epaper-frame/assets/154940519/4f26712a-f590-4b00-bb5e-5cda1b18fa73)<br>
![IMG_3029](https://github.com/Rocky56gh9/multimode-epaper-frame/assets/154940519/3601b0cc-f83a-4c9f-8129-23f4e5cfa830)<br>
![IMG_3030](https://github.com/Rocky56gh9/multimode-epaper-frame/assets/154940519/42c69998-81f5-487a-b612-998d50545a1a)<br>
![IMG_3028](https://github.com/Rocky56gh9/multimode-epaper-frame/assets/154940519/75bac938-558b-4085-966a-9d3847c5cbf5)<br>

# Equipment List
I have set up Amazon referral links to all of the components I used, which were all sourced from Amazon, if you don't mind using those links.

1. Option 1: [Raspberry Pi Zero WH](https://amzn.to/4aOmxIN) - This is an older version of the RPi, but the headers are already installed, so it's good to go out of the box. Slower than the Zero 2 W (below) but perfectly fine for this project.
2. Option 2: [Raspberry Pi Zero 2 W](https://amzn.to/3SdooQ2), [GPIO Pins (x2) and Installation Module](https://amzn.to/3vwNxfP) - For later versions of the project, I am using a Raspberry Pi Zero 2 W, which is notably faster, but the headers are sold separately and you need to install them manually. I found it to be quite easy to do so.
3. [Extra 40-Pin GPIO Solderless Header](https://amzn.to/3tFY4Vs)
4. [64 GB MicroSD Card](https://amzn.to/3Sc6vku)
5. [A/C Power adapter for MicroUSB](https://amzn.to/3TW36aX) OR [USB-A to MicroUSB](https://amzn.to/3NXCYbV) for powering from computer
6. [Waveshare 7.5" Tri-Color e-Paper Display with HAT Module](https://amzn.to/48PiB8I)
7. (Optional) [MicroUSB to Ethernet adapter](https://amzn.to/3RURdPJ) - Only needed if you will not be setting up wireless. This dongle is plug-and-play.
8. [Adafruit RaspberryPi Zero case](https://amzn.to/48sagbr)
9. [5x7 Desktop Picture Frame with paper mat insert](https://amzn.to/3tJUklN) for housing the screen for display. The mat will need to be modified later to fit the screen dimensions.

# New Build Guide

1. **Obtain APIs**
You will need to obtain API keys for the following services, which will be set later via configuration scripts.

**Reddit**<br>
How to Obtain New Reddit API Credentials

**Step 1**: Create a Reddit Account
If you don't already have a Reddit account, you need to create one.

Go to Reddit's Sign Up page.
Follow the instructions to create a new account.

**Step 2**: Create a Reddit Application
Once you have a Reddit account, you can create an application to get your API credentials.

Go to Reddit's Apps page.
Scroll down to the "Developed Applications" section.
Click on the "Create App" or "Create Another App" button.

**Step 3**: Fill in the Application Details
You will be prompted to fill in some details about your application.

Name: Give your application a name (e.g., "My Reddit App").
App Type: Select "script".
Description: (Optional) You can add a brief description of your application.
About URL: (Optional) You can leave this blank or add a URL related to your application.
Redirect URI: Enter http://localhost:8080.
Permissions: Select the permissions your app needs (leave it as default for most cases).

**Step 4**: Save and Retrieve Credentials
After filling in the details, click on the "Create app" button. Your app will be created, and you'll be shown your credentials.

Client ID: This is the string just under the name of your application (it's a long string of letters and numbers).
Client Secret: This is the secret key displayed next to "secret".
User Agent: This is a string that identifies your application, like MyRedditApp by /u/your_reddit_username.

**Step 5**: Save Your Credentials
Make sure to save your Client ID, Client Secret, and User Agent somewhere safe. You will need to manually add these credentials to your device later.

2. **Configure SD Card:**
   - Use the Raspberry Pi Imager.
   - Install RaspberryPi OS (Legacy, 64-bit) Lite
   - Set a hostname, ID, and unique password.
   - Add your network SSID and password.
   - Enable SSH on the second tab.

3. **Initial Setup:**
   - Insert the SD card into the Pi and power it up.
   - Wait ~10 minutes for it to appear on your network.
   - Log into your router, find the Pi, and note its IP address.

4. **SSH Login:**
   - Open Terminal and run: `ssh [unit name]@[IP address]`
   - Enter the password and follow prompts.
   - If restarting, reset the SSH key with: `ssh-keygen -R {RPi-IP-Address}`

5. **Install Git**
   - `sudo apt-get install git -y`

6. **Clone Repository:**
   - Run: `git clone https://github.com/Rocky56gh9/multimode-epaper-frame.git`

7. **Setup Script:**
   - Navigate to the directory: `cd multimode-epaper-frame`
   - Make the setup script executable and run the script: `chmod +x setup.sh && ./setup.sh`

The setup script installs all of the necessary packages and enables access to the device from a local machine over USB using Gadget mode. Access the device over USB: `ssh [username]@[unit name].local`<br>

# Configuration
Navigate to the `config` folder and run each of the configuration scripts. Each script will prompt you for the credentials necessary for the scripts. The scripts are:
1. dadjokes_config.py
2. showerthoughts_config.py
3. weatherstation_config.py
4. network_config.py

# Physical Assembly
1. The 7.5" screen fits well in the frame with paper mat listed in the equipment list, but requires modifying the size of the paper mat. Here are the measurements for the size of the mat needed to cover the non-display parts of the e-paper screen. These are measured from the exterior edge of the mat:
•	Top: 14mm<br>
•	Bottom: 16mm<br>
•	Left/Right: 7mm<br>

Remove the excess material as marked, and the remaining material should cover the non-display area of the screen. Carefully place the screen on the mat, ensure alignment, and tape the screen (from the back) to the mat to hold in place. Put the mat and screen into the frame and add the back. With the specific frame I used, the ribbon cable fits nicely through the bottom to the exterior of the frame. For now, I used an elastic to gather the excess ribbon material. I installed the RPi in the case (linked) and then glued the case to the rear of the frame.

That's it!
