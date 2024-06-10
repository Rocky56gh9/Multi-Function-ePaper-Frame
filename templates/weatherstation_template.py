#!/usr/bin/env python3

import sys
import os
import requests
import pytz
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime as dt
from timezonefinder import TimezoneFinder

# Correct path to the waveshare_epd library
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'e-Paper/RaspberryPi_JetsonNano/python/lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

from waveshare_epd import epd7in5b_V2

# OpenWeather API configuration
api_key = "{api_key}"
zip_code = "{zip_code}"
country_code = "{country_code}"

def fetch_weather_data():
    current_url = f"https://api.openweathermap.org/data/2.5/weather?zip={ZIP_CODE},{COUNTRY_CODE}&appid={API_KEY}&units=imperial"
    forecast_url = f"https://api.openweathermap.org/data/2.5/onecall?lat={{lat}}&lon={{lon}}&exclude=minutely,alerts&appid={API_KEY}&units=imperial"

    current_response = requests.get(current_url)
    if current_response.status_code == 200:
        weather_data = current_response.json()
        lat = weather_data['coord']['lat']
        lon = weather_data['coord']['lon']

        # Determine the time zone based on latitude and longitude
        tf = TimezoneFinder()
        time_zone_str = tf.timezone_at(lat=lat, lng=lon)
        timezone = pytz.timezone(time_zone_str)

        forecast_response = requests.get(forecast_url.format(lat=lat, lon=lon))
        sunrise_time, sunset_time = None, None

        if forecast_response.status_code == 200:
            sunrise_time = dt.fromtimestamp(weather_data['sys']['sunrise'], tz=timezone).strftime('%-I:%M%p')
            sunset_time = dt.fromtimestamp(weather_data['sys']['sunset'], tz=timezone).strftime('%-I:%M%p')
            return weather_data, forecast_response.json(), sunrise_time, sunset_time, time_zone_str
        else:
            print(f"Error fetching forecast data from OpenWeather: {forecast_response.status_code}")
            return None, None, None, None, None
    else:
        print(f"Error fetching current data from OpenWeather: {current_response.status_code}")
        return None, None, None, None, None

def wrap_text(text, max_width, font):
    words = text.split()
    lines = []
    while words:
        line = ''
        while words and font.getsize(line + words[0])[0] <= max_width:
            line += words.pop(0) + ' '
        lines.append(line)
    return lines

def calculate_fit_text(weather_data, font_path, initial_font_size, max_width, max_height, additional_line_spacing):
    font_size = initial_font_size
    while font_size > 12:  # Minimum font size
        font = ImageFont.truetype(font_path, font_size)
        forecast_texts = []
        combined_height = 0

        for period in weather_data["daily"][:5]:  # Next 5 days
            day_name = dt.fromtimestamp(period['dt']).strftime('%A')
            temp_high = int(period['temp']['max'])
            temp_low = int(period['temp']['min'])
            forecast_detail = f"{day_name}: {period['weather'][0]['description'].capitalize()}, High: {temp_high}°F, Low: {temp_low}°F"
            wrapped_text = wrap_text(forecast_detail, max_width, font)
            forecast_texts.append(wrapped_text)

            for line in wrapped_text:
                combined_height += font.getsize(line)[1] + additional_line_spacing

        if combined_height + additional_line_spacing * len(forecast_texts) <= max_height:
            return forecast_texts, font
        font_size -= 1  # Reduce font size and try again

    return [], ImageFont.truetype(font_path, 12)  # If no suitable size is found, return the smallest size

def draw_on_display(epd, current_data, forecast_texts, font, sunrise_time, sunset_time, location_name):
    image = Image.new('1', (epd.width, epd.height), 255)
    red_image = Image.new('1', (epd.width, epd.height), 255)
    draw_black = ImageDraw.Draw(image)
    draw_red = ImageDraw.Draw(red_image)

    title_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 32)
    date_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 28)
    header_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 30)
    content_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 24)
    sunrise_sunset_title_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 26)
    sunrise_sunset_time_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 22)

    title = f"Weather for {location_name}"
    current_date = dt.now().strftime("%A, %B %-d, %Y")
    title_x = (epd.width - draw_black.textsize(title, font=title_font)[0]) // 2
    date_x = (epd.width - draw_red.textsize(current_date, font=date_font)[0]) // 2
    draw_red.text((title_x, 10), title, font=title_font, fill=0)
    draw_black.text((date_x, 60), current_date, font=date_font, fill=0)

    left_column_width = epd.width // 3 - 10
    right_column_start = left_column_width + 20
    buffer_space = 10  # Reduced buffer space between title and content

    current_y = 120

    # Left Column - Current Conditions
    current_conditions_title = "Current Conditions:"
    wrapped_title = wrap_text(current_conditions_title, left_column_width, header_font)
    for line in wrapped_title:
        draw_red.text((10, current_y), line, font=header_font, fill=0)
        current_y += header_font.getsize(line)[1]

    current_y += buffer_space // 2

    current_conditions = current_data['weather'][0]['description'].capitalize()
    current_temp = f"{int(current_data['main']['temp'])}°F"
    full_conditions = f"{current_conditions}, {current_temp}"
    lines = wrap_text(full_conditions, left_column_width, content_font)
    for line in lines:
        draw_black.text((10, current_y), line, font=content_font, fill=0)
        current_y += content_font.getsize(line)[1]

    # Right Column - 5-Day Forecast
    forecast_y = 120
    draw_red.text((right_column_start, forecast_y), "5-Day Forecast:", font=header_font, fill=0)
    forecast_y += header_font.getsize("5-Day Forecast:")[1] + buffer_space

    additional_line_spacing = 9

    for day_forecast in forecast_texts:
        for line in day_forecast:
            if forecast_y + font.getsize(line)[1] + additional_line_spacing < epd.height - 20:
                draw_black.text((right_column_start, forecast_y), line, font=font, fill=0)
                forecast_y += font.getsize(line)[1] + additional_line_spacing
            else:
                break

    # Sunrise and Sunset
    sunrise_start_y = current_y + 100
    sunset_start_y = current_y + 150

    # Define the y-axis offsets for the sunrise and sunset times
    sunrise_time_y_offset = 5  # Adjust as needed
    sunset_time_y_offset = 5   # Adjust as needed

    draw_red.text((10, sunrise_start_y), "Sunrise: ", font=sunrise_sunset_title_font, fill=0)
    sunrise_time_x = 7 + draw_black.textsize("Sunrise: ", font=sunrise_sunset_title_font)[0]
    draw_black.text((sunrise_time_x, sunrise_start_y + sunrise_time_y_offset), sunrise_time, font=sunrise_sunset_time_font, fill=0)

    draw_red.text((10, sunset_start_y), "Sunset: ", font=sunrise_sunset_title_font, fill=0)
    sunset_time_x = 7 + draw_black.textsize("Sunset: ", font=sunrise_sunset_title_font)[0]
    draw_black.text((sunset_time_x, sunset_start_y + sunset_time_y_offset), sunset_time, font=sunrise_sunset_time_font, fill=0)

    epd.display(epd.getbuffer(image), epd.getbuffer(red_image))
    epd.sleep()

def main():
    epd = epd7in5b_V2.EPD()
    epd.init()

    current_weather_data, forecast_weather_data, sunrise_time, sunset_time, time_zone_str = fetch_weather_data()
    if current_weather_data and forecast_weather_data:
        max_forecast_height = epd.height - 120 - 30
        additional_line_spacing = 8

        left_column_width = epd.width // 3 - 10
        right_column_start = left_column_width + 20

        # Calculate the maximum width for the right column
        max_width = epd.width - right_column_start - 5  # Subtract 5 pixels for the buffer

        initial_font_size = 24  # Adjust this as needed for the starting font size

        forecast_texts, adjusted_font = calculate_fit_text(
            forecast_weather_data, 
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 
            initial_font_size, 
            max_width, 
            max_forecast_height,
            additional_line_spacing
        )

        draw_on_display(epd, current_weather_data, forecast_texts, adjusted_font, sunrise_time, sunset_time, current_weather_data['name'])

if __name__ == "__main__":
    main()
