#!/bin/bash

# Define the network interface to check. For example, this could be 'eth0', 'wlan0', etc.
INTERFACE="wlan0"
REPO_DIR="/home/bbb/bbb/"
LOGFILE="/home/bbb/startup_script.log"

# Wait for the network interface to come up.
until ping -c 1 github.com; do
    echo "Waiting for network..." >> "$LOGFILE"
    sleep 5
done

cd "$REPO_DIR" && git pull >> "$LOGFILE" 2>&1
# Start the Bridger Bowl Blinker
python3 bbb.py &

