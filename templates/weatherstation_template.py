#!/usr/bin/python
# -*- coding:utf-8 -*-

import sys
import os
import requests
import logging
import datetime
import time
from PIL import Image, ImageDraw, ImageFont
from timezonefinder import TimezoneFinder
from pytz import timezone
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

from waveshare_epd import epd7in5b_V2

home_dir = os.getenv('HOME')
image_path = f"{home_dir}/multimode-epaper-frame/images/weather.bmp"

# Logging setup
logging.basicConfig(level=logging.DEBUG)

# OpenWeather API configuration
api_key = '{api_key}'
zip_code = '{zip_code}'

# Fetch location data using zip code
def get_location_data(zip_code, api_key):
    url = f'http://api.openweathermap.org/data/2.5/weather?zip={zip_code},us&appid={api_key}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['coord']['lat'], data['coord']['lon'], data['name']
    else:
        raise Exception("Error fetching location data")

lat, lon, location_name = get_location_data(zip_code, api_key)
logging.info(f"Fetched location data: {location_name} (Lat: {lat}, Lon: {lon})")

# Get timezone based on latitude and longitude
tf = TimezoneFinder()
timezone_str = tf.timezone_at(lat=lat, lng=lon)
local_tz = timezone(timezone_str)

# Functions
def calculate_text_size(text, font):
    dummy_image = Image.new('1', (1, 1))
    draw = ImageDraw.Draw(dummy_image)
    return draw.textsize(text, font)

def adjust_font_size_and_wrap(text, font_path, max_width, max_height, max_font_size):
    font_size = min(38, max_font_size)  # Start with the smaller of 38 or max_font_size
    while font_size > 12:  # Minimum font size
        font = ImageFont.truetype(font_path, font_size)
        lines = wrap_text(text, font, max_width)
        text_height = sum([calculate_text_size(line, font)[1] for line in lines]) + len(lines) * 5
        if text_height <= max_height:
            break
        font_size -= 2
    return font, lines

def wrap_text(text, font, max_width):
    words = text.split()
    lines = []
    current_line = ''
    for word in words:
        line_width, _ = calculate_text_size(current_line + word, font)
        if line_width <= max_width:
            current_line += word + ' '
        else:
            lines.append(current_line.strip())
            current_line = word + ' '
    lines.append(current_line.strip())
    return lines

# Main script
try:
    # e-Paper display initialization
    epd = epd7in5b_V2.EPD()
    epd.init()
    epd.Clear()

    # Fetch weather data
    url = f'http://api.openweathermap.org/data/2.5/weather?zip={zip_code},us&appid={api_key}&units=imperial'
    response = requests.get(url)
    weather_data = response.json()

    temp = weather_data['main']['temp']
    weather_description = weather_data['weather'][0]['description']
    logging.info(f"Fetched weather data: {temp}F, {weather_description}")

    # Create images for drawing
    black_image = Image.new('1', (800, 480), 255)
    red_image = Image.new('1', (800, 480), 255)
    draw_black = ImageDraw.Draw(black_image)
    draw_red = ImageDraw.Draw(red_image)

    # Load and paste header image
    header_image_path = f"{home_dir}/multimode-epaper-frame/images/weather.bmp"
    header_image = Image.open(header_image_path)
    header_image = header_image.resize((80, 80))

    # Create a horizontally mirrored image
    mirrored_header_image = header_image.transpose(Image.FLIP_LEFT_RIGHT)

    # Define positions for the images
    positions = [(25, 0), (695, 0), (25, 400), (695, 400)]  # Top left, top right, bottom left, bottom right

    # Paste the original image at top left and bottom left positions
    for pos in [positions[0], positions[2]]:
        black_image.paste(header_image, pos)

    # Paste the mirrored image at top right and bottom right positions
    for pos in [positions[1], positions[3]]:
        black_image.paste(mirrored_header_image, pos)

    # Font paths
    title_font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
    body_font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    footer_font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

    # Title setup
    title_font_size = 50  # Starting font size for title
    title_text = f"Weather for {location_name}"
    title_font = ImageFont.truetype(title_font_path, title_font_size)

    # Footer setup
    footer_text = datetime.datetime.now(local_tz).strftime("%A, %B %-d, %Y")
    footer_font = ImageFont.truetype(footer_font_path, 32)

    # Draw title and footer
    title_width, title_height = calculate_text_size(title_text, title_font)
    title_x = (800 - title_width) // 2
    title_y = 15
    draw_red.text((title_x, title_y), title_text, font=title_font, fill=0)

    footer_width, footer_height = calculate_text_size(footer_text, footer_font)
    footer_x = (800 - footer_width) // 2
    footer_y = 415
    draw_red.text((footer_x, footer_y), footer_text, font=footer_font, fill=0)

    # Calculate areas for weather info
    text_area_start = title_y + title_height + 10
    text_area_end = footer_y - 10
    max_text_height = text_area_end - text_area_start
    max_text_width = 780

    # Weather info text
    weather_text = f"Temperature: {temp}F\nCondition: {weather_description}"
    weather_font, wrapped_weather_text = adjust_font_size_and_wrap(weather_text, body_font_path, max_text_width, max_text_height, title_font_size)

    # Draw weather info
    y = text_area_start
    for line in wrapped_weather_text:
        draw_black.text((20, y), line, font=weather_font, fill=0)
        y += weather_font.getsize(line)[1] + 5

    # Display the images
    epd.display(epd.getbuffer(black_image), epd.getbuffer(red_image))
    time.sleep(2)

except IOError as e:
    logging.error(e)

except KeyboardInterrupt:
    logging.info("ctrl + c:")
    epd7in5b_V2.epdconfig.module_exit()
    exit()
