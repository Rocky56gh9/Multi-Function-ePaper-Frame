#!/usr/bin/python
# -*- coding:utf-8 -*-

import sys
import os
from PIL import Image
import logging

# Correct path to the waveshare_epd library
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'e-Paper/RaspberryPi_JetsonNano/python/lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

# Logging setup
logging.basicConfig(level=logging.DEBUG)

# Import the waveshare_epd module
from waveshare_epd import epd7in5b_V2

def resize_image(image, target_width, target_height):
    """Resize image while maintaining aspect ratio."""
    original_width, original_height = image.size
    ratio = min(target_width / original_width, target_height / original_height)
    new_width = int(original_width * ratio)
    new_height = int(original_height * ratio)
    return image.resize((new_width, new_height), Image.ANTIALIAS), new_width, new_height

def main():
    try:
        # e-Paper display initialization
        epd = epd7in5b_V2.EPD()
        epd.init()
        epd.Clear()

        # Load the image
        home_dir = os.getenv('HOME')
        image_path = f"{home_dir}/multimode-epaper-frame/images/sleep.bmp"
        image = Image.open(image_path)

        # Resize the image to fit the display
        target_width = 800
        target_height = 480
        image, new_width, new_height = resize_image(image, target_width, target_height)

        # Convert the image to 1-bit color for the black channel
        image = image.convert('1')

        # Create blank images for drawing
        black_image = Image.new('1', (800, 480), 255)  # Black image
        red_image = Image.new('1', (800, 480), 255)    # Red image (not used in this case)

        # Center the image
        x = (target_width - new_width) // 2
        y = (target_height - new_height) // 2

        # Paste the image onto the black image
        black_image.paste(image, (x, y))

        # Display the images
        epd.display(epd.getbuffer(black_image), epd.getbuffer(red_image))

    except IOError as e:
        logging.error(e)

    except KeyboardInterrupt:
        logging.info("ctrl + c:")
        epd7in5b_V2.epdconfig.module_exit()
        exit()

if __name__ == '__main__':
    main()
