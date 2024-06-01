import sys
import os
import requests
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from bs4 import BeautifulSoup

libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)
from waveshare_epd import epd7in5b_V2

user_sunsign = "virgo"

home_dir = os.getenv('HOME')
image_dir = f"{home_dir}/multimode-epaper-frame/images"

def fetch_horoscope_from_api(sunsign):
    url = f"https://www.usatoday.com/horoscopes/daily/{sunsign}/"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        horoscope_section = soup.find('section', class_='sign')
        horoscope_text = ''
        if horoscope_section:
            paragraphs = horoscope_section.find_all_next('p', limit=2)
            for p in paragraphs:
                horoscope_text += p.get_text(strip=True) + ' '
        return horoscope_text.strip()
    else:
        raise Exception(f"Webpage Request Failed: Status Code {response.status_code}")

def find_optimal_font_size(text, max_width, max_height, font_path):
    font_size = 30  # Starting font size
    smallest_acceptable_font_size = 10
    step = 1

    while font_size >= smallest_acceptable_font_size:
        font = ImageFont.truetype(font_path, int(font_size))
        wrapped_text, text_height = wrap_text(text, font, max_width, max_height)

        if text_height <= max_height:
            return font, wrapped_text
        else:
            font_size -= step

    # Fallback to the smallest font size if necessary
    font = ImageFont.truetype(font_path, smallest_acceptable_font_size)
    wrapped_text, _ = wrap_text(text, font, max_width, max_height)
    return font, wrapped_text

def calculate_character_limits(font_path, font_size, text_area_width, text_area_height):
    font = ImageFont.truetype(font_path, font_size)
    sample_char_width, line_height = font.getsize('W')
    max_chars_per_line = text_area_width // sample_char_width
    max_lines = text_area_height // line_height
    return max_chars_per_line, max_lines

def wrap_text(text, font, max_width):
    words = text.split()
    lines = []
    current_line = ''

    for word in words:
        test_line = current_line + (' ' if current_line else '') + word
        test_width = font.getsize(test_line)[0]

        if test_width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines

def resize_image(image, target_width, target_height):
    original_width, original_height = image.size
    ratio = min(target_width / original_width, target_height / original_height)
    new_width = int(original_width * ratio)
    new_height = int(original_height * ratio)
    return image.resize((new_width, new_height), Image.ANTIALIAS)

def draw_on_display(zodiac_image, horoscope_text, epd):
    header_font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
    header_font_size = 50
    header_color = "red"
    header_y_position = 5
    header_font = ImageFont.truetype(header_font_path, header_font_size)

    date_font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
    date_font_size = 35
    date_color = "black"
    date_y_position = 70
    date_font = ImageFont.truetype(date_font_path, date_font_size)

    font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    font_size = 25
    image_area_width = epd.width // 3
    header_area_height = header_font_size + 5
    date_area_height = date_font_size + 25
    text_area_width = epd.width - image_area_width
    text_area_height = epd.height - header_area_height - date_area_height

    max_chars_per_line, max_lines = calculate_character_limits(
        font_path, font_size, text_area_width, text_area_height
    )

    font = ImageFont.truetype(font_path, font_size)
    lines = wrap_text(horoscope_text, font, max_chars_per_line * font.getsize('W')[0])

    image_width = epd.width // 3
    image_y_position = 190
    zodiac_resized = resize_image(zodiac_image, image_width, epd.height - image_y_position)

    text_start_x = image_width
    text_start_y = date_y_position + date_font_size + 50
    text_width = epd.width - text_start_x
    available_height = epd.height - text_start_y

    image_black = Image.new('1', (epd.width, epd.height), 255)
    image_red = Image.new('1', (epd.width, epd.height), 255)
    draw_black = ImageDraw.Draw(image_black)
    draw_red = ImageDraw.Draw(image_red)

    title = f"Daily Horoscope - {sunsign.capitalize()}"
    title_x = (epd.width - draw_black.textsize(title, font=header_font)[0]) // 2
    header_draw = draw_red if header_color == "red" else draw_black
    header_draw.text((title_x, header_y_position), title, font=header_font, fill=0)

    current_date = datetime.now().strftime("%A, %B %-d, %Y")
    date_x = (epd.width - draw_black.textsize(current_date, font=date_font)[0]) // 2
    date_draw = draw_red if date_color == "red" else draw_black
    date_draw.text((date_x, date_y_position), current_date, font=date_font, fill=0)

    image_red.paste(zodiac_resized, (0, image_y_position))

    text_y = text_start_y
    for line in lines:
        draw_black.text((text_start_x + 10, text_y), line, font=font, fill=0)
        text_y += font.getsize(line)[1] + 5

    epd.display(epd.getbuffer(image_black), epd.getbuffer(image_red))
    epd.sleep()

def main():
    try:
        horoscope_text = fetch_horoscope_from_api(sunsign)

        epd = epd7in5b_V2.EPD()
        epd.init()

        zodiac_image_path = f"{image_dir}/{sunsign}.bmp"
        zodiac_image = Image.open(zodiac_image_path)

        draw_on_display(zodiac_image, horoscope_text, epd)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
