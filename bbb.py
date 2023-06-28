from blinkstick import blinkstick
import requests
import json
import datetime
import time
import logging
from logging.handlers import RotatingFileHandler
import traceback

WEATHER_ATTRIBUTE = "wind"
STATION = "alpine"
TARGET_WEATHER_ATTRIBUTE_VALUE = 2
POLL_INTERVAL = 600  # seconds
URL = "https://api.bridgerbowl.com/graphql"
MAX_RETRIES = 6
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


def check_weather_at_bridger_bowl():
    now = datetime.datetime.now()
    # start_time is an hour before now
    start_time = (now - datetime.timedelta(hours=1, minutes=0)).strftime("%Y-%m-%d %H:%M:%S")
    end_time = now.strftime("%Y-%m-%d %H:%M:%S")
    variables = {"station": STATION, "date_start": start_time, "date_end": end_time}
    payload = {"query": QUERY, "variables": variables, "headers": HEADERS}

    logger.info("Station:    " + STATION)
    logger.info("Attribute:  " + WEATHER_ATTRIBUTE)
    logger.info("Target:     " + str(TARGET_WEATHER_ATTRIBUTE_VALUE))
    logger.info("Start time: " + start_time)
    logger.info("End time:   " + end_time)

    for attempt in range(MAX_RETRIES):
        logger.info("Fetching weather data, attempt " + str(attempt + 1) + " of " + str(MAX_RETRIES))
        try:
            response = requests.post(URL, json=payload)
            response.raise_for_status()  # Raises error for unsuccessful status (i.e., not 2xx).
            weather_data = json.loads(response.text)
            logger.info("Latest weather data: %s", json.dumps(weather_data, indent=4)
            return (weather_data["data"]["weather_readings"]["data"][0][WEATHER_ATTRIBUTE] > TARGET_WEATHER_ATTRIBUTE_VALUE)
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            logger.error("Failed to fetch new weather data. Exception: %s", e)
            if attempt < MAX_RETRIES - 1:  # i.e. if it's not the final attempt
                time.sleep(2**attempt)  # exponential backoff
            else:
                raise  # raise the last exception


### Main ###
try:
    logger = logging.getLogger("Rotating Log")
    logger.setLevel(logging.DEBUG)
    handler = RotatingFileHandler("/home/bbb/bbb.log", maxBytes=1000000, backupCount=5)
    logger.addHandler(handler)

    led = blinkstick.find_first()

    if led is None:
        logging.error("BlinkStick not found. Exiting.")
    else:
        while True:
            if check_weather_at_bridger_bowl():
                logger.info("Target weather condition met!")
                # Each pulse is approximately 2s
                led.pulse(name="blue", repeats=POLL_INTERVAL // 2)
            else:
                logger.info("Target weather condition not met.")
                led.set_color(name="white")
                time.sleep(POLL_INTERVAL)
            logger.info("--------------------------------------")
except KeyboardInterrupt:
    logger.info("Interrupted by user. Exiting... Bye!")
    led.turn_off()
except Exception as e:
    error_traceback = traceback.format_exc()  # Capture the full traceback
    logger.error("Exiting with exception: %s", e)
    logger.error("Full traceback: %s", error_traceback)  # Log the traceback
    led.set_color(name="red")
