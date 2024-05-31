import os

# Template for the horoscope script
HOROSCOPE_TEMPLATE = """import sys
import os
import requests
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import textwrap

libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)
from waveshare_epd import epd7in5b_V2

# Sun Sign Configuration
sunsign = "{sun_sign}"

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
        raise Exception(f"Webpage Request Failed: Status Code {{response.status_code}}")

# Initialize the e-Paper display
epd = epd7in5b_V2.EPD()
epd.init()
epd.Clear()

# Fetch horoscope text
horoscope_text = fetch_horoscope_from_api(sunsign)

# Create images for drawing
black_image = Image.new('1', (800, 480), 255)
red_image = Image.new('1', (800, 480), 255)
draw_black = ImageDraw.Draw(black_image)
draw_red = ImageDraw.Draw(red_image)

# Font paths
header_font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
body_font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

# Title setup
title_font_size = 50  # Starting font size for title
title_text = f"{sunsign.capitalize()} Horoscope"
title_font = ImageFont.truetype(header_font_path, title_font_size)

# Footer setup
footer_text = datetime.now().strftime("%A, %B %-d, %Y")
footer_font = ImageFont.truetype(body_font_path, 32)

# Draw title and footer
title_width, title_height = draw_red.textsize(title_text, title_font)
title_x = (800 - title_width) // 2
title_y = 15
draw_red.text((title_x, title_y), title_text, font=title_font, fill=0)

footer_width, footer_height = draw_red.textsize(footer_text, footer_font)
footer_x = (800 - footer_width) // 2
footer_y = 415
draw_red.text((footer_x, footer_y), footer_text, font=footer_font, fill=0)

# Horoscope text setup
horoscope_font = ImageFont.truetype(body_font_path, 30)
horoscope_text_lines = textwrap.wrap(horoscope_text, width=80)
y_text = title_y + title_height + 20
for line in horoscope_text_lines:
    width, height = draw_black.textsize(line, horoscope_font)
    draw_black.text(((800 - width) // 2, y_text), line, font=horoscope_font, fill=0)
    y_text += height

# Display the images
epd.display(epd.getbuffer(black_image), epd.getbuffer(red_image))
epd.sleep()

except IOError as e:
    print(e)

except KeyboardInterrupt:
    print("ctrl + c:")
    epd7in5b_V2.epdconfig.module_exit()
    exit()
"""

VALID_SUN_SIGNS = [
    "aries", "taurus", "gemini", "cancer",
    "leo", "virgo", "libra", "scorpio",
    "sagittarius", "capricorn", "aquarius", "pisces"
]

def configure_horoscopes():
    print("Configuring Horoscopes")
    print("Valid sun signs are:")
    print(", ".join(VALID_SUN_SIGNS))
    num_horoscopes = int(input("How many unique horoscopes do you want to display? "))
    for i in range(num_horoscopes):
        while True:
            sun_sign = input(f"Enter the sun sign for horoscope {i+1}: ").strip().lower()
            if sun_sign in VALID_SUN_SIGNS:
                break
            else:
                print(f"Invalid sun sign. Please enter a valid sun sign from the list: {', '.join(VALID_SUN_SIGNS)}")
        script_content = HOROSCOPE_TEMPLATE.format(sun_sign=sun_sign)
        script_path = f'scripts/horoscope_{sun_sign}.py'
        with open(script_path, 'w') as file:
            file.write(script_content)
        print(f"Generated script for {sun_sign} horoscope: {script_path}")

def main():
    print("Horoscope Configuration Interface")
    configure_horoscopes()

if __name__ == "__main__":
    main()
