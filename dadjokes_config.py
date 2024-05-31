import os

# Template for the dad jokes script
DADJOKES_TEMPLATE = """import sys
import os
import praw
import logging
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)
from waveshare_epd import epd7in5b_V2

# Reddit API Configuration
client_id = "{client_id}"
client_secret = "{client_secret}"
user_agent = "{user_agent}"

# Logging setup
logging.basicConfig(level=logging.DEBUG)

def fetch_dad_joke():
    reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent=user_agent)
    subreddit = reddit.subreddit("dadjokes")
    top_post = next(subreddit.top(time_filter='day', limit=1))
    return top_post.title, top_post.selftext

def draw_dad_joke(epd, joke_title, joke_body):
    # Create images for drawing
    black_image = Image.new('1', (800, 480), 255)
    red_image = Image.new('1', (800, 480), 255)
    draw_black = ImageDraw.Draw(black_image)
    draw_red = ImageDraw.Draw(red_image)

    # Font paths
    title_font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
    body_font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

    # Title setup
    title_font = ImageFont.truetype(title_font_path, 50)
    body_font = ImageFont.truetype(body_font_path, 30)

    # Draw title and body
    draw_red.text((20, 20), joke_title, font=title_font, fill=0)
    draw_black.text((20, 100), joke_body, font=body_font, fill=0)

    # Display the images
    epd.display(epd.getbuffer(black_image), epd.getbuffer(red_image))

def main():
    try:
        epd = epd7in5b_V2.EPD()
        epd.init()
        epd.Clear()

        joke_title, joke_body = fetch_dad_joke()
        draw_dad_joke(epd, joke_title, joke_body)

    except IOError as e:
        logging.error(e)

    except KeyboardInterrupt:
        logging.info("ctrl + c:")
        epd7in5b_V2.epdconfig.module_exit()
        exit()

if __name__ == "__main__":
    main()
"""

def configure_dadjokes():
    print("Configuring Dad Jokes Script")
    client_id = input("Enter your Reddit API client ID: ")
    client_secret = input("Enter your Reddit API client secret: ")
    user_agent = input("Enter your Reddit API user agent: ")
    script_content = DADJOKES_TEMPLATE.format(client_id=client_id, client_secret=client_secret, user_agent=user_agent)
    script_path = 'scripts/dadjokes.py'
    with open(script_path, 'w') as file:
        file.write(script_content)
    print(f"Generated dad jokes script: {script_path}")

def main():
    print("Dad Jokes Configuration Interface")
    configure_dadjokes()

if __name__ == "__main__":
    main()
