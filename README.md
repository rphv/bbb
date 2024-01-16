# Bridger Bowl Blinker

The Bridger Bowl Blinker is a standalone device based built on the [Raspberry Pi Zero W](https://www.raspberrypi.com/products/raspberry-pi-zero-w/) that displays animations on an [LED grid](https://learn.adafruit.com/adafruit-charlieplex-bonnet/overview) when certain weather conditions are met at [Bridger Bowl](https://bridgerbowl.com/weather/history-tables).

If there's new snow at the top of Bridger lift, a pulsing (blinking) animation with falling "snowflake" pixels is displayed. Each falling pixel represents 1 inch (rounded up) of  new snow, e.g. 1 pixel = 1 inch, 2 pixels = 2 inches, etc.

If there's no new snow, but the wind at Midway is > 4 mph, sideways "blowing" pixels are shown. Each pixel represents 1 mph above 4, e.g. 1 pixel = 5 mph, 2 pixels = 6 mph, etc.

## Usage

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

If your network requires a username & password (e.g., for a university wifi network), use the following in wpa_supplicant.conf:

```
country=US
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="your_network_name"
    scan_ssid=1
    key_mgmt=WPA-EAP
    identity="your_username"
    password="your_password"
    eap=PEAP
    phase1="peaplabel=0"
    phase2="auth=MSCHAPV2"
}
```

Replace `your_network_name` and `your_username` / `your_password` with the network SSID and username/password of your wifi network.

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
