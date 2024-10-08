#!/usr/bin/env python3

import sys
import os
import praw
import logging
import datetime
import time
from PIL import Image, ImageDraw, ImageFont

# Path to the waveshare_epd library
libdir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'e-Paper', 'RaspberryPi_JetsonNano', 'python', 'lib'))
if os.path.exists(libdir):
    sys.path.append(libdir)

from waveshare_epd import epd7in5b_V2

home_dir = os.getenv('HOME')
image_path = f"{home_dir}/multimode-epaper-frame/images/runningshower.bmp"

# Logging setup
logging.basicConfig(level=logging.DEBUG)

# Functions
def calculate_text_size(text, font):
    dummy_image = Image.new('1', (1, 1))
    draw = ImageDraw.Draw(dummy_image)
    return draw.textsize(text, font)

def adjust_font_size_and_wrap(text, font_path, initial_font_size, max_width, max_height):
    font_size = initial_font_size
    font = ImageFont.truetype(font_path, font_size)
    lines = wrap_text(text, font, max_width)
    text_height = sum([calculate_text_size(line, font)[1] for line in lines])

    while (text_height > max_height) and font_size > 12:
        font_size -= 2
        font = ImageFont.truetype(font_path, font_size)
        lines = wrap_text(text, font, max_width)
        text_height = sum([calculate_text_size(line, font)[1] for line in lines])

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
    epd = epd7in5b_V2.EPD()
    epd.init()
    epd.Clear()

    reddit = praw.Reddit(client_id='{client_id}',
                         client_secret='{client_secret}',
                         user_agent='{user_agent}')

    # Subreddit name
    subreddit_name = "Showerthoughts"
    subreddit = reddit.subreddit(subreddit_name)

    def fetch_top_post(subreddit, time_filter):
        try:
            top_post = next(subreddit.top(time_filter=time_filter, limit=1))
            logging.info("Fetched post: " + top_post.title)
            return top_post
        except StopIteration:
            logging.info(f"No posts found in subreddit {subreddit.display_name} for the time filter '{time_filter}'.")
            return None

    # Try to fetch the top post from the last hour
    top_post = fetch_top_post(subreddit, 'hour')

    # If no post is found, try to fetch the top post from today
    if top_post is None:
        top_post = fetch_top_post(subreddit, 'day')

    # If still no post is found, handle it accordingly
    if top_post is not None:
        print(f"Title: {top_post.title}")
        print(f"Score: {top_post.score}")
        print(f"URL: {top_post.url}")
    else:
        print("No posts found for the specified time filters.")

    black_image = Image.new('1', (800, 480), 255)
    red_image = Image.new('1', (800, 480), 255)
    draw_black = ImageDraw.Draw(black_image)
    draw_red = ImageDraw.Draw(red_image)

    # Load and paste header image
    header_image_path = f"{home_dir}/multimode-epaper-frame/images/runningshower.bmp"
    header_image = Image.open(header_image_path)
    header_image = header_image.resize((80, 80))

    # Create a horizontally mirrored image
    mirrored_header_image = header_image.transpose(Image.FLIP_LEFT_RIGHT)

    # Define positions for the images
    positions = [(25, 0), (25, 400), (695, 0), (695, 400)]

    # Paste the original image at top right and bottom right positions
    for pos in [positions[2], positions[3]]:
        black_image.paste(header_image, pos)

    # Paste the mirrored image at top left and bottom left positions
    for pos in [positions[0], positions[1]]:
        black_image.paste(mirrored_header_image, pos)

    # Font paths
    title_font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
    body_font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    footer_font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

    # Title setup
    title_font_size = 42  # Starting font size for title
    title_text = "Reddit Shower Thoughts"
    title_font = ImageFont.truetype(title_font_path, title_font_size)

    # Footer setup
    footer_text = datetime.datetime.now().strftime("%A, %B %-d, %Y")
    footer_font = ImageFont.truetype(footer_font_path, 32)

    # Draw title and footer
    title_x, title_y = 110, 10
    draw_red.text((title_x, title_y), title_text, font=title_font, fill=0)

    footer_width, footer_height = calculate_text_size(footer_text, footer_font)
    footer_x = (800 - footer_width) // 2
    footer_y = 415
    draw_red.text((footer_x, footer_y), footer_text, font=footer_font, fill=0)

    # Calculate areas for post title and body
    text_area_limit = 390  # Example: 390 pixels from the top
    max_text_width = 780
    max_text_height = text_area_limit - 110
    initial_font_size = 38

    # Adjust post title font size and wrap text
    post_title_font, wrapped_post_title = adjust_font_size_and_wrap(top_post.title, body_font_path, initial_font_size, max_text_width, max_text_height)

    # Draw post title
    y = 110
    for line in wrapped_post_title:
        draw_black.text((20, y), line, font=post_title_font, fill=0)
        y += post_title_font.getsize(line)[1] + 5

    # Display the images
    epd.display(epd.getbuffer(black_image), epd.getbuffer(red_image))
    time.sleep(2)

except IOError as e:
    logging.error(e)

except KeyboardInterrupt:
    logging.info("ctrl + c:")
    epd7in5b_V2.epdconfig.module_exit()
    exit()
