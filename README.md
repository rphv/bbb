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

The repository includes a bash script `rc.local` that clones this repository and starts the Python script.
It is designed to be copied to the /etc directory of the target Raspberry Pi & executed on boot.

On start, Bridger Bowl's graphql endpoint is queried to fetch the amount of new snow at the top of the Bridger lift. If there's any new snow, a pulsing "falling pixel" animation is started on the LED grid. The number of falling pixels is set to the number of inches of new snow (rounded up). If there's no new snow, the windspeed is checked at the Bridger lift midway station. If the windspeed is greater than 4 mph, a "blowing pixel" animation is started on the LED grid. The number of blowing pixels is the difference between the current windspeed and 4 mph.

If neither target weather condition is met, the display is turned off.

The endpoint is queried at a configurable interval (default 10 min) to refresh the weather data. If an endpoint request fails, it will be retried up to MAX_RETRIES with an exponential backoff.

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

A single illuminated pixel in the corner of the display indicates an error condition and signals a need to reboot.

A rotating log `bbb.log` is written to the home directory.

## Variations

An implementation for a [BlinkStick](https://www.blinkstick.com/) can be found on the branch `blinkstick_driver`.
