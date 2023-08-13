# Bridger Bowl Blinker

A Python script to display "falling snowflakes" on a [Charlieplex LED Bonnet](https://learn.adafruit.com/adafruit-charlieplex-bonnet/overview) when there's new snow at [Bridger Bowl](https://bridgerbowl.com/weather/history-tables) ski area.

## Usage

This script is designed to be run on a [Raspberry Pi Zero W](https://www.raspberrypi.com/products/raspberry-pi-zero-w/) running Raspbian 11 (Bullseye).

The Pi Zero can be configured for a specific wifi network by writing a file called `wpa_supplicant.conf` with wifi credentials to the root of the Raspberry Pi's bootable SD card.

#### wpa_supplicant.conf
```
country=US
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="your_network_name"
    psk="your_password"
    key_mgmt=WPA-PSK
}
```

Replace `your_network_name` and `your_password` with the network SSID and password of your wifi network.

## Implementation

The repository includes a bash script `pull_and_start_bbb.sh` that pulls the latest code from this repository and starts the Python script.
It is designed to be run on boot via an entry in /etc/rc.local, e.g.:
```
sudo -u bbb /home/bbb/bbb/pull_and_start_bbb.sh &
```

On start, Bridger Bowl's graphql endpoint is queried to fetch the current weather conditions at a specific weather station. If the request fails, it will be retried up to MAX_RETRIES with an exponential backoff.

The endpoint is queried at a configurable interval (default 10 min) to refresh the weather data.

Valid values for Bridger Bowl weather stations include:

- alpine
- base
- bridger
- midway
- ridge
- schlasmans
- cabin
- snowflake
- deerpark

Not all stations record all weather attributes.

If the target weather condition is met, a "falling pixel" animation is started on the LED bonnet. The number of falling pixels is determined by the difference between the target weather attribute value and the current conditions. In the default implementation, the number of falling pixels corresponds to the number of inches of new snow.

If the target weather condition is not met, the display is turned off.

A single illuminated pixel in the corner of the display indicates an error condition and signals a need to reboot.

A rotating log `bbb.log` is written to the home directory.

## Variations

An implementation for a [BlinkStick](https://www.blinkstick.com/) can be found on the branch `blinkstick_driver`.

