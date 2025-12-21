#!/usr/bin/env python3

import sys
import os
import time
import datetime
import logging
from typing import Optional, Iterable

import praw
from PIL import Image, ImageDraw, ImageFont

# -----------------------------
# Waveshare epd lib path
# -----------------------------
libdir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "e-Paper", "RaspberryPi_JetsonNano", "python", "lib")
)
if os.path.exists(libdir):
    sys.path.append(libdir)

from waveshare_epd import epd7in5b_V2  # noqa: E402

# -----------------------------
# Paths / Logging
# -----------------------------
HOME = os.getenv("HOME", "")
PROJECT_DIR = os.path.join(HOME, "multimode-epaper-frame")
LOG_DIR = os.path.join(PROJECT_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

LOG_PATH = os.path.join(LOG_DIR, "showerthoughts.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH),
        logging.StreamHandler(sys.stdout),
    ],
)

# -----------------------------
# Reddit credentials
# -----------------------------
# Replace these OR leave placeholders if your config generator injects them.
CLIENT_ID = "{client_id}"
CLIENT_SECRET = "{client_secret}"
USER_AGENT = "{user_agent}"

SUBREDDIT_NAME = "Showerthoughts"

TOP_TIMEFILTERS = ["hour", "day", "week", "month", "year", "all"]

# -----------------------------
# Rendering helpers
# -----------------------------
def calculate_text_size(text: str, font: ImageFont.FreeTypeFont):
    dummy_image = Image.new("1", (1, 1))
    draw = ImageDraw.Draw(dummy_image)
    return draw.textsize(text, font)

def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int):
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        line_width, _ = calculate_text_size(current_line + word, font)
        if line_width <= max_width:
            current_line += word + " "
        else:
            lines.append(current_line.strip())
            current_line = word + " "
    if current_line.strip():
        lines.append(current_line.strip())
    return lines

def adjust_font_size_and_wrap(text: str, font_path: str, initial_font_size: int, max_width: int, max_height: int):
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

def render_error_screen(epd, message: str):
    try:
        black_image = Image.new("1", (800, 480), 255)
        red_image = Image.new("1", (800, 480), 255)
        draw_black = ImageDraw.Draw(black_image)
        draw_red = ImageDraw.Draw(red_image)

        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 34)
        body_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)

        draw_red.text((20, 20), "Shower Thoughts Error", font=title_font, fill=0)

        lines = wrap_text(message, body_font, 760)
        y = 80
        for line in lines[:14]:
            draw_black.text((20, y), line, font=body_font, fill=0)
            y += body_font.getsize(line)[1] + 6

        epd.display(epd.getbuffer(black_image), epd.getbuffer(red_image))
        time.sleep(2)
        epd.sleep()
    except Exception as e:
        logging.exception("Failed to render error screen: %s", e)

# -----------------------------
# Reddit fetch logic
# -----------------------------
def _first_valid(posts: Iterable) -> Optional[object]:
    """
    Return first non-stickied post from an iterable of PRAW submissions.
    """
    for p in posts:
        try:
            if getattr(p, "stickied", False):
                continue
            # Sometimes a "submission" can be weird; ensure it has a title
            title = getattr(p, "title", None)
            if not title:
                continue
            return p
        except Exception:
            continue
    return None

def fetch_post(subreddit) -> Optional[object]:
    """
    Primary: subreddit.top with widening time filters.
    Secondary: subreddit.hot.
    """
    # Top ladder
    for tf in TOP_TIMEFILTERS:
        try:
            cand = _first_valid(subreddit.top(time_filter=tf, limit=10))
            if cand is not None:
                logging.info("Selected via TOP: time_filter=%s title=%r score=%s", tf, cand.title, getattr(cand, "score", "?"))
                return cand
            logging.warning("No valid posts via TOP for time_filter=%s", tf)
        except Exception as e:
            logging.exception("TOP fetch failed for time_filter=%s: %s", tf, e)

    # Hot fallback
    try:
        cand = _first_valid(subreddit.hot(limit=20))
        if cand is not None:
            logging.info("Selected via HOT fallback: title=%r score=%s", cand.title, getattr(cand, "score", "?"))
            return cand
        logging.error("No valid posts via HOT fallback either.")
    except Exception as e:
        logging.exception("HOT fallback fetch failed: %s", e)

    return None

# -----------------------------
# Main
# -----------------------------
def main():
    logging.info("==== showerthoughts.py START ====")

    # Init display
    epd = epd7in5b_V2.EPD()
    epd.init()

    # DO NOT Clear() up front; if we crash after clearing, you get a blank screen.
    # Only clear right before a successful render, or in error rendering.
    # epd.Clear()

    # Init reddit
    try:
        reddit = praw.Reddit(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            user_agent=USER_AGENT,
        )
        subreddit = reddit.subreddit(SUBREDDIT_NAME)
    except Exception as e:
        logging.exception("Failed to init PRAW: %s", e)
        render_error_screen(epd, f"PRAW init failed: {e}")
        logging.info("==== showerthoughts.py END ====")
        return

    # Fetch post
    top_post = fetch_post(subreddit)
    if top_post is None:
        msg = f"No posts returned from r/{SUBREDDIT_NAME} via TOP({', '.join(TOP_TIMEFILTERS)}) or HOT."
        logging.error(msg)
        render_error_screen(epd, msg)
        logging.info("==== showerthoughts.py END ====")
        return

    # Render
    try:
        epd.Clear()

        black_image = Image.new("1", (800, 480), 255)
        red_image = Image.new("1", (800, 480), 255)
        draw_black = ImageDraw.Draw(black_image)
        draw_red = ImageDraw.Draw(red_image)

        # Load and paste header image
        header_image_path = os.path.join(PROJECT_DIR, "images", "runningshower.bmp")
        header_image = Image.open(header_image_path).resize((80, 80))
        mirrored_header_image = header_image.transpose(Image.FLIP_LEFT_RIGHT)

        positions = [(25, 0), (25, 400), (695, 0), (695, 400)]
        for pos in [positions[2], positions[3]]:
            black_image.paste(header_image, pos)
        for pos in [positions[0], positions[1]]:
            black_image.paste(mirrored_header_image, pos)

        # Fonts
        title_font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        body_font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        footer_font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

        title_font = ImageFont.truetype(title_font_path, 42)
        footer_font = ImageFont.truetype(footer_font_path, 32)

        # Title and footer
        title_text = "Reddit Shower Thoughts"
        draw_red.text((110, 10), title_text, font=title_font, fill=0)

        try:
            footer_text = datetime.datetime.now().strftime("%A, %B %-d, %Y")
        except Exception:
            footer_text = datetime.datetime.now().strftime("%A, %B %d, %Y")

        footer_width, _ = calculate_text_size(footer_text, footer_font)
        footer_x = (800 - footer_width) // 2
        draw_red.text((footer_x, 415), footer_text, font=footer_font, fill=0)

        # Post title wrapping
        text_area_limit = 390
        max_text_width = 780
        max_text_height = text_area_limit - 110
        initial_font_size = 38

        post_title_font, wrapped_post_title = adjust_font_size_and_wrap(
            top_post.title, body_font_path, initial_font_size, max_text_width, max_text_height
        )

        y = 110
        for line in wrapped_post_title:
            draw_black.text((20, y), line, font=post_title_font, fill=0)
            y += post_title_font.getsize(line)[1] + 5

        epd.display(epd.getbuffer(black_image), epd.getbuffer(red_image))
        time.sleep(2)
        epd.sleep()

        logging.info("Rendered post: title=%r score=%s", top_post.title, getattr(top_post, "score", "?"))

    except Exception as e:
        logging.exception("Render/display failed: %s", e)
        render_error_screen(epd, f"Render failed: {e}")

    logging.info("==== showerthoughts.py END ====")

if __name__ == "__main__":
    main()
