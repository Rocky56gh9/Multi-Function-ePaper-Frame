#!/usr/bin/env python3
import sys
import os
import json
import time
import glob
import argparse
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from PIL import Image, ImageDraw, ImageFont

try:
    from zoneinfo import ZoneInfo  # Python 3.9+
except Exception:
    ZoneInfo = None

# Waveshare epd lib path (project-relative)
libdir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "e-Paper", "RaspberryPi_JetsonNano", "python", "lib")
)
if os.path.exists(libdir):
    sys.path.append(libdir)

from waveshare_epd import epd7in5b_V2

# -----------------------------
# Constants
# -----------------------------
API_URL = "https://api.api-ninjas.com/v1/horoscope"
CACHE_KEEP_DAYS = 30
TZ_NAME = "America/New_York"

VALID_SIGNS = {
    "aries","taurus","gemini","cancer","leo","virgo","libra","scorpio",
    "sagittarius","capricorn","aquarius","pisces"
}

# -----------------------------
# Paths
# -----------------------------
HOME = os.getenv("HOME", "")
PROJECT_DIR = os.path.join(HOME, "multimode-epaper-frame")
IMAGE_DIR = os.path.join(PROJECT_DIR, "images")
CACHE_DIR = os.path.join(PROJECT_DIR, "cache")
CONFIG_DIR = os.path.join(PROJECT_DIR, "config")
SECRETS_PATH = os.path.join(CONFIG_DIR, "secrets.json")
SCHEDULE_PATH = os.path.join(CONFIG_DIR, "horoscope_schedule.json")

os.makedirs(CACHE_DIR, exist_ok=True)

# -----------------------------
# Time helpers
# -----------------------------
def _now_local() -> datetime:
    if ZoneInfo is not None:
        try:
            return datetime.now(ZoneInfo(TZ_NAME))
        except Exception:
            pass
    return datetime.now()

def _today_str() -> str:
    return _now_local().strftime("%Y-%m-%d")

def _yesterday_str() -> str:
    return (_now_local() - timedelta(days=1)).strftime("%Y-%m-%d")

# -----------------------------
# Config helpers
# -----------------------------
def _load_json(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r") as f:
            return json.load(f) or {}
    except Exception:
        return {}

def _get_api_key() -> str:
    # Prefer env var if set
    env_key = os.getenv("API_NINJAS_KEY", "").strip()
    if env_key:
        return env_key

    data = _load_json(SECRETS_PATH)
    key = (data.get("API_NINJAS_KEY") or "").strip()
    if key:
        return key

    raise RuntimeError("Missing API Ninjas key. Run config/horoscope_config.py or set API_NINJAS_KEY.")

def _pick_sign_from_schedule(now: datetime) -> str:
    """
    Supports two schedule modes in config/horoscope_schedule.json:

    Mode A (rotation):
      {"mode":"rotation","signs":["scorpio","sagittarius","taurus"]}

      Uses hour-of-day modulo len(signs).

    Mode B (hour_map):
      {"mode":"hour_map","hours":{"0":"scorpio","1":"sagittarius","2":"taurus",...}}

      Uses local hour directly; if missing, falls back to "default" if present.
    """
    cfg = _load_json(SCHEDULE_PATH)
    mode = (cfg.get("mode") or "rotation").strip()

    if mode == "hour_map":
        hours = cfg.get("hours") or {}
        # keys might be strings
        h = str(now.hour)
        sign = (hours.get(h) or hours.get(int(now.hour), None) or hours.get("default"))
        if isinstance(sign, str) and sign.lower() in VALID_SIGNS:
            return sign.lower()
        # fall back to rotation if misconfigured
        mode = "rotation"

    signs = cfg.get("signs") or []
    signs = [s.lower().strip() for s in signs if isinstance(s, str)]
    signs = [s for s in signs if s in VALID_SIGNS]

    if not signs:
        # safe default if nothing configured
        return "scorpio"

    return signs[now.hour % len(signs)]

# -----------------------------
# Cache helpers
# -----------------------------
def _cache_path(sign: str, date_str: str) -> str:
    return os.path.join(CACHE_DIR, f"horoscope_{sign}_{date_str}.json")

def _load_cache(sign: str, date_str: str) -> Optional[str]:
    p = _cache_path(sign, date_str)
    if not os.path.exists(p):
        return None
    try:
        with open(p, "r") as f:
            data = json.load(f) or {}
        text = (data.get("text") or "").strip()
        return text if text else None
    except Exception:
        return None

def _save_cache(sign: str, date_str: str, text: str) -> None:
    payload = {
        "provider": "api-ninjas",
        "sign": sign,
        "date": date_str,
        "fetched_at_local": _now_local().isoformat(),
        "text": text,
    }
    try:
        with open(_cache_path(sign, date_str), "w") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def _prune_cache(sign: str) -> None:
    pattern = os.path.join(CACHE_DIR, f"horoscope_{sign}_*.json")
    files = glob.glob(pattern)
    if not files:
        return
    cutoff = _now_local() - timedelta(days=CACHE_KEEP_DAYS)
    cutoff_date = cutoff.replace(hour=0, minute=0, second=0, microsecond=0)
    for fp in files:
        base = os.path.basename(fp)
        try:
            date_part = base.rsplit("_", 1)[-1].replace(".json", "")
            file_date = datetime.strptime(date_part, "%Y-%m-%d")
            if file_date < cutoff_date:
                try:
                    os.remove(fp)
                except Exception:
                    pass
        except Exception:
            continue

# -----------------------------
# API fetch + cached fetch
# -----------------------------
def _fetch_from_api(sign: str) -> str:
    key = _get_api_key()
    headers = {
        "X-Api-Key": key,
        "Accept": "application/json",
        "User-Agent": "multimode-epaper-frame/1.0",
    }
    params = {"zodiac": sign}

    attempts = 4
    base_sleep = 1.0
    last_exc = None

    for i in range(attempts):
        try:
            r = requests.get(API_URL, headers=headers, params=params, timeout=(5, 12))

            if r.status_code == 429:
                retry_after = r.headers.get("Retry-After")
                if retry_after:
                    try:
                        time.sleep(float(retry_after))
                    except Exception:
                        time.sleep(base_sleep * (2 ** i))
                else:
                    time.sleep(base_sleep * (2 ** i))
                continue

            r.raise_for_status()
            data = r.json() or {}
            text = (data.get("horoscope") or "").strip()
            if not text:
                raise RuntimeError("API Ninjas response missing 'horoscope' field.")
            return text

        except Exception as e:
            last_exc = e
            if i < attempts - 1:
                time.sleep(base_sleep * (2 ** i))

    raise RuntimeError(f"API Ninjas fetch failed after {attempts} attempts. Last error: {last_exc}")

def fetch_horoscope_cached(sign: str) -> str:
    _prune_cache(sign)
    today = _today_str()

    cached = _load_cache(sign, today)
    if cached:
        return cached

    try:
        text = _fetch_from_api(sign)
        _save_cache(sign, today, text)
        return text
    except Exception:
        y = _yesterday_str()
        cached_y = _load_cache(sign, y)
        if cached_y:
            return cached_y
        raise

# -----------------------------
# Text layout helpers
# -----------------------------
def _text_width(font: ImageFont.FreeTypeFont, s: str) -> int:
    bbox = font.getbbox(s)
    return bbox[2] - bbox[0]

def _line_height(font: ImageFont.FreeTypeFont) -> int:
    bbox = font.getbbox("Ag")
    return bbox[3] - bbox[1]

def wrap_text_pixels(text: str, font: ImageFont.FreeTypeFont, max_width_px: int) -> List[str]:
    words = text.split()
    lines: List[str] = []
    current = ""
    for w in words:
        candidate = (current + " " + w).strip()
        if _text_width(font, candidate) <= max_width_px:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines

def fit_text_to_box(text: str, font_path: str, max_size: int, min_size: int,
                    box_w: int, box_h: int, line_spacing: int = 3):
    for size in range(max_size, min_size - 1, -1):
        font = ImageFont.truetype(font_path, size)
        lines = wrap_text_pixels(text, font, box_w)
        lh = _line_height(font)
        total_h = len(lines) * lh + max(0, len(lines) - 1) * line_spacing
        if total_h <= box_h:
            return font, lines

    # Truncate at min size with ellipsis
    font = ImageFont.truetype(font_path, min_size)
    lh = _line_height(font)
    max_lines = max(1, (box_h + line_spacing) // (lh + line_spacing))
    lines = wrap_text_pixels(text, font, box_w)
    if len(lines) <= max_lines:
        return font, lines

    lines = lines[:max_lines]
    ell = "…"
    last = lines[-1].rstrip()
    while last and _text_width(font, last + ell) > box_w:
        last = last[:-1].rstrip()
    lines[-1] = (last + ell) if last else ell
    return font, lines

def resize_image(image, target_width, target_height):
    original_width, original_height = image.size
    ratio = min(target_width / original_width, target_height / original_height)
    new_width = int(original_width * ratio)
    new_height = int(original_height * ratio)
    return image.resize((new_width, new_height), Image.ANTIALIAS)

# -----------------------------
# Rendering
# -----------------------------
def draw_on_display(sign: str, zodiac_image, horoscope_text: str, epd):
    header_font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    header_font_size = 50
    header_color = "red"
    header_y_position = 5
    header_font = ImageFont.truetype(header_font_path, header_font_size)

    date_font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    date_font_size = 35
    date_color = "black"
    date_y_position = 70
    date_font = ImageFont.truetype(date_font_path, date_font_size)

    body_font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

    # Layout tuned for 800x400
    image_width = epd.width // 3
    image_y_position = 160

    text_start_x = image_width + 10
    text_start_y = date_y_position + date_font_size + 30

    text_box_w = epd.width - text_start_x - 10
    text_box_h = epd.height - text_start_y - 10

    image_black = Image.new("1", (epd.width, epd.height), 255)
    image_red = Image.new("1", (epd.width, epd.height), 255)
    draw_black = ImageDraw.Draw(image_black)
    draw_red = ImageDraw.Draw(image_red)

    title = f"Daily Horoscope - {sign.capitalize()}"
    title_x = (epd.width - draw_black.textsize(title, font=header_font)[0]) // 2
    (draw_red if header_color == "red" else draw_black).text(
        (title_x, header_y_position), title, font=header_font, fill=0
    )

    try:
        current_date = _now_local().strftime("%A, %B %-d, %Y")
    except Exception:
        current_date = _now_local().strftime("%A, %B %d, %Y")
    date_x = (epd.width - draw_black.textsize(current_date, font=date_font)[0]) // 2
    (draw_red if date_color == "red" else draw_black).text(
        (date_x, date_y_position), current_date, font=date_font, fill=0
    )

    zodiac_resized = resize_image(zodiac_image, image_width, epd.height - image_y_position)
    image_red.paste(zodiac_resized, (0, image_y_position))

    body_font, lines = fit_text_to_box(
        horoscope_text, body_font_path,
        max_size=25, min_size=14,
        box_w=text_box_w, box_h=text_box_h,
        line_spacing=3
    )

    y = text_start_y
    lh = _line_height(body_font)
    for line in lines:
        draw_black.text((text_start_x, y), line, font=body_font, fill=0)
        y += lh + 3
        if y > epd.height - 10:
            break

    epd.display(epd.getbuffer(image_black), epd.getbuffer(image_red))
    epd.sleep()

# -----------------------------
# Main
# -----------------------------
def main():
    parser = argparse.ArgumentParser(description="Render horoscope to Waveshare ePaper.")
    parser.add_argument("--sign", help="Zodiac sign (e.g., scorpio). If omitted, uses schedule config.")
    args = parser.parse_args()

    sign = (args.sign or "").strip().lower()
    if sign:
        if sign not in VALID_SIGNS:
            raise SystemExit(f"Invalid sign '{sign}'. Valid: {', '.join(sorted(VALID_SIGNS))}")
    else:
        sign = _pick_sign_from_schedule(_now_local())

    # Fetch horoscope (cached daily per sign)
    horoscope_text = fetch_horoscope_cached(sign)

    # Init display
    epd = epd7in5b_V2.EPD()
    epd.init()

    zodiac_image_path = os.path.join(IMAGE_DIR, f"{sign}.bmp")
    if not os.path.exists(zodiac_image_path):
        raise SystemExit(f"Missing zodiac image: {zodiac_image_path}")

    zodiac_image = Image.open(zodiac_image_path)

    draw_on_display(sign, zodiac_image, horoscope_text, epd)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
