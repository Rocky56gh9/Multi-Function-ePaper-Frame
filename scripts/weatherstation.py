import sys
import os
import requests
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import pytz
from timezonefinder import TimezoneFinder
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)
from waveshare_epd import epd7in5b_V2

# Function to get location based on IP address
def get_location():
    response = requests.get('https://ipinfo.io')
    data = response.json()
    location = data['loc'].split(',')
    city = data['city']
    return float(location[0]), float(location[1]), city

# Get location details
latitude, longitude, city = get_location()

# Function to fetch weather data from OpenWeather API
def fetch_weather(api_key, latitude, longitude):
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&units=metric&appid={api_key}"
    response = requests.get(url)
    return response.json()

# Function to fetch timezone from latitude and longitude
def get_timezone(latitude, longitude):
    tf = TimezoneFinder()
    return tf.timezone_at(lat=latitude, lng=longitude)

# API key for OpenWeather (add your OpenWeather API key here)
api_key = 'YOUR_OPENWEATHER_API_KEY'

# Fetch weather data
weather_data = fetch_weather(api_key, latitude, longitude)

# Extract relevant weather information
weather_main = weather_data['weather'][0]['main']
temperature = weather_data['main']['temp']
humidity = weather_data['main']['humidity']
wind_speed = weather_data['wind']['speed']

# Get timezone and current time in local timezone
timezone_str = get_timezone(latitude, longitude)
timezone = pytz.timezone(timezone_str)
current_time = datetime.now(timezone)

# Initialize the e-Paper display
epd = epd7in5b_V2.EPD()
epd.init()
epd.Clear()

# Create images for drawing
black_image = Image.new('1', (800, 480), 255)
red_image = Image.new('1', (800, 480), 255)
draw_black = ImageDraw.Draw(black_image)
draw_red = ImageDraw.Draw(red_image)

# Font paths
title_font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
body_font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
footer_font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

# Title setup
title_font_size = 50  # Starting font size for title
title_text = f"Conditions & Forecast - {city}"
title_font = ImageFont.truetype(title_font_path, title_font_size)

# Footer setup
footer_text = current_time.strftime("%A, %B %-d, %Y")
footer_font = ImageFont.truetype(footer_font_path, 32)

# Draw title and footer
title_width, title_height = draw_red.textsize(title_text, title_font)
title_x = (800 - title_width) // 2
title_y = 15
draw_red.text((title_x, title_y), title_text, font=title_font, fill=0)

footer_width, footer_height = draw_red.textsize(footer_text, footer_font)
footer_x = (800 - footer_width) // 2
footer_y = 415
draw_red.text((footer_x, footer_y), footer_text, font=footer_font, fill=0)

# Weather information setup
info_font = ImageFont.truetype(body_font_path, 30)
weather_text = f"Main: {weather_main}\nTemperature: {temperature}°C\nHumidity: {humidity}%\nWind Speed: {wind_speed} m/s"
draw_black.text((20, title_y + title_height + 20), weather_text, font=info_font, fill=0)

# Display the images
epd.display(epd.getbuffer(black_image), epd.getbuffer(red_image))
epd.sleep()

except IOError as e:
    print(e)

except KeyboardInterrupt:
    print("ctrl + c:")
    epd7in5b_V2.epdconfig.module_exit()
    exit()
