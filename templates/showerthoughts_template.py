import sys
import os
import praw
import logging
import datetime
import time
from PIL import Image, ImageDraw, ImageFont

# Path to the waveshare_epd library
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'e-Paper/RaspberryPi_JetsonNano/python/lib')
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

    # Reddit API setup
    reddit = praw.Reddit(client_id='{client_id}',
                         client_secret='{client_secret}',
                         user_agent='{user_agent}')

    subreddit = reddit.subreddit("Showerthoughts")
    top_post = next(subreddit.top(time_filter='hour', limit=1))
    logging.info("Fetched post: " + top_post.title)

    # Create images for drawing
    black_image = Image.new('1', (800, 480), 255)
    red_image = Image.new('1', (800, 480), 255)
    draw_black = ImageDraw.Draw(black_image)
    draw_red = ImageDraw.Draw(red_image)

    # Load and paste header image
    header_image_path = f"{home_dir}/multimode-epaper-frame/images/showerthought.bmp"
    header_image = Image.open(header_image_path)
    header_image = header_image.resize((80, 80))

    # Create a horizontally mirrored image
    mirrored_header_image = header_image.transpose(Image.FLIP_LEFT_RIGHT)

    # Define positions for the images
    positions = [(20, 0), (690, 0), (20, 400), (690, 400)]  # Top left, top right, bottom left, bottom right

    # Paste the original image at top left and bottom left positions
    for pos in [positions[1], positions[3]]:
        black_image.paste(header_image, pos)

    # Paste the mirrored image at top right and bottom right positions
    for pos in [positions[0], positions[2]]:
        black_image.paste(mirrored_header_image, pos)

    # Font paths
    title_font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
    body_font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    footer_font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

    # Title setup
    title_font_size = 40  # Starting font size for title
    title_text = "Reddit Shower Thoughts"
    title_font = ImageFont.truetype(title_font_path, title_font_size)

    # Footer setup
    footer_text = datetime.datetime.now().strftime("%A, %B %-d, %Y")
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

    # Calculate areas for post title and body
    text_area_start = title_y + title_height + 10
    text_area_end = footer_y - 10
    max_text_height = text_area_end - text_area_start
    max_text_width = 780

    # Adjust post title and body font sizes and wrap text
    post_title_font, wrapped_post_title = adjust_font_size_and_wrap(top_post.title, title_font_path, max_text_width, max_text_height // 3, title_font_size)
    post_body_font, wrapped_post_body = adjust_font_size_and_wrap(top_post.selftext, body_font_path, max_text_width, max_text_height * 2 // 3, post_title_font.size)

    # Draw post title and body
    y = text_area_start
    for line in wrapped_post_title:
        draw_black.text((20, y), line, font=post_title_font, fill=0)
        y += post_title_font.getsize(line)[1] + 5

    y += 10  # Space between title and body
    for line in wrapped_post_body:
        draw_black.text((20, y), line, font=post_body_font, fill=0)
        y += post_body_font.getsize(line)[1] + 5

    # Display the images
    epd.display(epd.getbuffer(black_image), epd.getbuffer(red_image))
    time.sleep(2)

except IOError as e:
    logging.error(e)

except KeyboardInterrupt:
    logging.info("ctrl + c:")
    epd7in5b_V2.epdconfig.module_exit()
    exit()
