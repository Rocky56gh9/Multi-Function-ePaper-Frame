# Multimode e-Paper Frame
This e-paper multi-function display project uses a number of techniques for retrieving, formatting, and displaying content on a low-power e-Paper display.

On a pre-programmed schedule, each of these will be displayed:
   1. Reddit Dad Joke top entry
   2. Reddit Shower Thoughts top entry
   3. Weather Station with location name, current conditions, 5-day forecast, and local sunrise/sunset times
   4. Daily Horoscope
   5. Sleep image

This project was my first attempt at any kind of coding and is entirely self-taught using ChatGPT-4. All images used in the project are AI-generated via DALL-E.

The overall cost for the project materials is about $150 USD.

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
   - Go to the respective websites for Reddit and OpenWeather and create an account.
   - Follow the instructions to obtain your API keys.

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
   - Open Terminal and run:
   ```
   ssh [unit name]@[IP address]
   ```
   - Enter the password and follow prompts.
   - If necessary, reset the SSH keys with:
   ```sh
   ssh-keygen -R {RPi-IP-Address}
   ```
   or
   ```sh
   ssh-keygen - R {username.local}
   ```

6. **Install Components and Set Up Configurations**
   - Copy and paste the following into your terminal to install all necessary components, clone the repository, and run the configuration scripts automatically:
   
     ```sh
     curl -sSL https://raw.githubusercontent.com/Rocky56gh9/multimode-epaper-frame/main/setup_project.sh -o setup_project.sh && chmod +x setup_project.sh && ./setup_project.sh
     ```     
   - The setup script installs all of the necessary packages and enables access to the device from a local machine over USB using Gadget mode. <b>This will take quite a while to run</b>.
   - The script has built-in retries due to the number of dependencies that need to be installed. If you're still seeing errors or things are not working as expected, try running the ./setup.sh script again.
   - After installing all dependencies, the setup script will automatically call the required configuration scripts and templates and <b>prompt you for the inputs needed for the project</b>.

# Adding Your Configurations
Have this information in hand as the setup script runs, so you're ready to enter the data when prompted.

   - API keys
      - Reddit: client_id, client_secret, and user_agent
      - OpenWeather: API Key
    
   - Zip Code for Weather

   - Country Code: two-letter country code, e.g., "us"

   - Preferred Schedule
      - What time to start running scripts (24-hour, HH:MM)
      - What time to stop running scripts and display the sleep image (24-hour, HH:MM)
      - The e-Paper screen will refresh at the top of the hour, at 15 after the hour, at 30 after the hour, and at 45 after the hour, between the start and end times you enter. You can customize the order of what (e.g., Dad Jokes, Shower Thoughts, Horoscope, Weatherstation) displays at each milestone time.

<b>NOTE</b>: For the horoscopes, you can add as many as you'd like. The script will ask you for the one or more zodiac signs to include. The cron job will automatically distribute them across the day. For example, if you entered two zodiac signs and specified the horoscope to run at half past the hour, they would display in turn, at half past, throughout the day between your defined start and end times.

To change configurations after initial setup, navigate to the `config` folder to access the inidividual scripts. For example, if you want to change the location for the Weatherstation, run that configuration script to change the zip code.

# Physical Assembly
The 7.5" screen fits well in the frame with paper mat listed in the equipment list, but requires modifying the size of the paper mat. Here are the measurements for the size of the mat needed to cover the non-display parts of the e-paper screen. These are measured from the exterior edge of the mat:<br>
   - Top: 14mm<br>
   - Bottom: 16mm<br>
   - Left/Right: 7mm<br>

Remove the excess material as marked, and the remaining material should cover the non-display area of the screen. Carefully place the screen on the mat, ensure alignment, and tape the screen (from the back) to the mat to hold in place. Put the mat and screen into the frame and add the back. With the specific frame I used, the ribbon cable fits nicely through the bottom to the exterior of the frame. For now, I used an elastic to gather the excess ribbon material. I installed the RPi in the case (linked) and then glued the case to the rear of the frame.

Have fun!
