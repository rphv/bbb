# Bridger Bowl Blinker

A Python script to run a [BlinkStick](https://www.blinkstick.com/) when a given weather condition (e.g., new snow!) is met at [Bridger Bowl](https://bridgerbowl.com/weather/history-tables) ski area.

## Usage

This script is designed to be run on a [Raspberry Pi](https://www.raspberrypi.org/) running Raspbian 11 (Bullseye). The current implementation uses an [Ourlink USB WiFi module](https://www.adafruit.com/product/1012). This can be configured for a specific wifi network by writing a file called wpa_supplicant.conf with wifi credentials to the root of the Raspberry Pi's bootable SD card.

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

Replace "your_network_name" and "your_password" with the network SSID and password of your wifi network.
