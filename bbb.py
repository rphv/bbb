import time
import random
import board
import busio
import select
import sys
import math
import requests
import json
import datetime
import logging
from logging.handlers import RotatingFileHandler
import traceback

from adafruit_is31fl3731.charlie_bonnet import CharlieBonnet as Display


# constants and variables for the LED control
DELAY = 0.1
PULSE_LENGTH = 4.0
MIN_INTENSITY = 0
MAX_INTENSITY = 32

# constants for the endpoint request
POLL_INTERVAL = 600  # seconds
URL = "https://api.bridgerbowl.com/graphql"
MAX_RETRIES = 10
QUERY = """
query Query($station: String!, $date_start: DateTime!, $date_end: DateTime!) {
  weather_readings(
    station: $station
    date_range: { from: $date_start, to: $date_end }
  ) {
    data {
      date
      temperature
      wind
      gusts
      wind_direction
      humidity
      pressure
      new_snow
      total_snow
      water_content
    }
  }
}
"""
HEADERS = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "sec-ch-ua": '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "'macOS'",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "sec-gpc": "1",
    "Referer": "https://bridgerbowl.com/",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}
NO_DATA = -1

# setup for the LED display
i2c = busio.I2C(board.SCL, board.SDA)
display = Display(i2c)

def interruptible_sleep(seconds):
    select.select([], [], [], seconds)

def check_weather_at_bridger_bowl(weather_station, weather_attribute, target_weather_attribute_value):
    now = datetime.datetime.now()
    # start_time is an hour before now
    start_time = (now - datetime.timedelta(hours=1, minutes=0)).strftime("%Y-%m-%d %H:%M:%S")
    end_time = now.strftime("%Y-%m-%d %H:%M:%S")
    variables = {"station": weather_station, "date_start": start_time, "date_end": end_time}
    payload = {"query": QUERY, "variables": variables, "headers": HEADERS}

    logger.info("Station:    " + weather_station)
    logger.info("Attribute:  " + weather_attribute)
    logger.info("Target:     " + str(target_weather_attribute_value))
    logger.info("Start time: " + start_time)
    logger.info("End time:   " + end_time)

    for attempt in range(MAX_RETRIES):
        logger.info("Fetching weather data, attempt " + str(attempt + 1) + " of " + str(MAX_RETRIES))
        try:
            response = requests.post(URL, json=payload)
            response.raise_for_status()  # raises error for unsuccessful status (i.e., not 2xx).
            weather_data = json.loads(response.text)
            if not weather_data["data"]["weather_readings"]["data"]:
                logger.info("No weather data fetched from station: " + weather_station)
                return NO_DATA
            logger.info("Latest weather data: %s", json.dumps(weather_data["data"]["weather_readings"]["data"][0], indent=4))
            return math.ceil(weather_data["data"]["weather_readings"]["data"][0][weather_attribute])
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            logger.error("Failed to fetch new weather data. Exception: %s", e)
            if attempt < MAX_RETRIES - 1:  # i.e. if it's not the final attempt
                time.sleep(2**attempt)  # exponential backoff
            else:
                raise  # raise the last exception

def draw_snow_pixels(max_pixels):
    falling_pixels = []
    end_time = datetime.datetime.now() + datetime.timedelta(seconds=POLL_INTERVAL)
    start_time = time.time()
    while datetime.datetime.now() < end_time:
        elapsed_time = (time.time() - start_time) % PULSE_LENGTH  # time elapsed since the start of the while loop
        pulse_progress = elapsed_time / PULSE_LENGTH  # progress of the current pulse as a ratio
        intensity = int((MAX_INTENSITY - MIN_INTENSITY) * abs(2 * pulse_progress - 1) + MIN_INTENSITY)

        display.fill(intensity)

        # if we're below the max pixels, add a new one at a random x-position
        if len(falling_pixels) < max_pixels:
            falling_pixels.append((random.randint(0, display.width - 1), 0))

        # loop over a copy of the falling pixels list so we can modify it while looping
        for pixel in falling_pixels.copy():
            x, y = pixel

            # if this pixel has hit the bottom, remove it from the list
            if y >= display.height:
                falling_pixels.remove(pixel)
            else:
                # otherwise, move the pixel down and draw it
                display.pixel(x, y, 0)  # draw pixel with zero intensity, turning it off
                y += 1  # move pixel down
                falling_pixels[falling_pixels.index(pixel)] = (x, y)  # update pixel position in list

        interruptible_sleep(DELAY)


def draw_wind_pixels(max_pixels):
    falling_pixels = []
    end_time = datetime.datetime.now() + datetime.timedelta(seconds=POLL_INTERVAL)
    while datetime.datetime.now() < end_time:
        display.fill(0)

        # if we're below the max pixels, add a new one at a random y-position
        if len(falling_pixels) < max_pixels:
            falling_pixels.append((0, random.randint(0, display.height - 1)))

        # loop over a copy of the falling pixels list so we can modify it while looping
        for pixel in falling_pixels.copy():
            x, y = pixel

            # if this pixel has reached the right edge, remove it from the list
            if x >= display.width:
                falling_pixels.remove(pixel)
            else:
                # otherwise, move the pixel right and draw it
                display.pixel(x, y, MAX_INTENSITY) # turn pixel on
                x += 1 # move pixel right
                falling_pixels[falling_pixels.index(pixel)] = (x, y) # update pixel position in list

        interruptible_sleep(DELAY)


### main ###
try:
    logger = logging.getLogger("Rotating Log")
    logger.setLevel(logging.DEBUG)
    handler = RotatingFileHandler("/home/bbb/bbb.log", maxBytes=1000000, backupCount=5)
    logger.addHandler(handler)

    while True:
        target_new_snow_value = 0
        current_new_snow = check_weather_at_bridger_bowl("bridger", "new_snow", target_new_snow_value)
        if current_new_snow > target_new_snow_value:
            logger.info("It's snowing!")
            draw_snow_pixels(current_new_snow - target_new_snow_value)
        else:
            target_wind_value = 4
            current_wind = check_weather_at_bridger_bowl("midway", "wind", 4)
            if current_new_snow == NO_DATA and current_wind == NO_DATA:
                raise Exception("No data fetched from any station!")
            if current_wind > target_wind_value:
                logger.info("It's not snowing, but it IS windy.")
                draw_wind_pixels(current_wind - target_wind_value)
            else:
                logger.info("No exciting weather to display.")
                display.fill(0)
                time.sleep(POLL_INTERVAL)
        logger.info("--------------------------------------")

except KeyboardInterrupt:
    logger.info("Interrupted by user. Exiting... Bye!")
    display.fill(0)
    sys.exit(0)

except Exception as e:
    error_traceback = traceback.format_exc()  # capture the full traceback
    logger.error("Exiting with exception: %s", e)
    logger.error("Full traceback: %s", error_traceback)
    display.fill(0)
    display.pixel(0, 0, MAX_INTENSITY) # turn on one pixel to indicate an error
    sys.exit(0)

