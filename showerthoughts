#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
# Directory setup for waveshare_epd module
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)
from waveshare_epd import epd7in5b_V2
import time
import datetime
import praw
import logging
from PIL import Image, ImageDraw, ImageFont

# Directory setup for waveshare_epd module
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

logging.basicConfig(level=logging.DEBUG)

def calculate_text_size(text, font):
    dummy_image = Image.new('1', (1, 1))
    draw = ImageDraw.Draw(dummy_image)
    return draw.textsize(text, font)

def adjust_font_size_and_wrap(text, font_path, initial_font_size, max_width, max_height):
    font_size = initial_font_size
    font = ImageFont.truetype(font_path, font_size)
    lines = wrap_text(text, font, max_width)
    text_height = sum([calculate_text_size(line, font)[1] for line in lines])

    while (text_height > max_height) and font_size > 0:
        font_size -= 1
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

try:
    epd = epd7in5b_V2.EPD()
    epd.init()
    epd.Clear()

    reddit = praw.Reddit(client_id='[enter client id within single quotes]',
                         client_secret='[enter client secret within single quotes]',
                         user_agent='[enter whatever name you want]')

    subreddit = reddit.subreddit("Showerthoughts")
    top_post = next(subreddit.top(time_filter='hour', limit=1))
    logging.info("Fetched post: " + top_post.title)
    print("Fetched post:", top_post.title)

    black_image = Image.new('1', (800, 480), 255)
    red_image = Image.new('1', (800, 480), 255)
    draw_black = ImageDraw.Draw(black_image)
    draw_red = ImageDraw.Draw(red_image)

    # Load and place header image
    header_image_path = '[path to the image file]/runningshower.bmp'
    header_image = Image.open(header_image_path)
    header_image = header_image.resize((80, 80))

    # Create a mirrored image
    mirrored_header_image = header_image.transpose(Image.FLIP_LEFT_RIGHT)

    # Define positions for the images
    positions = [(25, 0), (25, 400), (695, 0), (695, 400)]  # Adjusted order of positions

    # Paste the original and mirrored images at specified positions
    for pos in positions:
        if pos[0] == 25:  # For top left and bottom left positions
            black_image.paste(mirrored_header_image, pos)
        else:  # For top left and bottom left positions
            black_image.paste(header_image, pos)

    # Title and footer settings
    title_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 42)
    title_text = "Reddit Shower Thoughts"
    title_x, title_y = 110, 10
    draw_red.text((title_x, title_y), title_text, font=title_font, fill=0)

    footer_font_size = 32
    footer_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', footer_font_size)
    footer_text = datetime.datetime.now().strftime("%A, %B %d, %Y")
    footer_width, footer_height = draw_black.textsize(footer_text, font=footer_font)
    footer_x = (800 - footer_width) // 2  # Center align
    footer_y = 415  # Adjust as needed
    draw_red.text((footer_x, footer_y), footer_text, font=footer_font, fill=0)
    # footer_x, footer_y = 125, 415
    # draw_black.text((footer_x, footer_y), footer_text, font=footer_font, fill=0)

    # Adjustable variable for text area limit
    # Adjust this to change where the text area ends (above the footer)
    text_area_limit = 390  # Example: 390 pixels from the top

    # Dynamic font size and text wrapping
    max_text_width = 780
    max_text_height = text_area_limit - 110  # Adjusted based on the text area limit
    initial_font_size = 38
    font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

    optimal_font, wrapped_text = adjust_font_size_and_wrap(top_post.title, font_path, initial_font_size, max_text_width, max_text_height)

    y = 110
    for line in wrapped_text:
        draw_black.text((20, y), line, font=optimal_font, fill=0)
        y += optimal_font.getsize(line)[1] + 5

    # Display the images
    epd.display(epd.getbuffer(black_image), epd.getbuffer(red_image))
    time.sleep(2)

except IOError as e:
    logging.error(e)

except KeyboardInterrupt:
    logging.info("ctrl + c:")
    epd7in5b_V2.epdconfig.module_exit()
    exit()
