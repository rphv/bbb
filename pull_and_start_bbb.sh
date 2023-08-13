#!/bin/bash

# Define the network interface to check. For example, this could be 'eth0', 'wlan0', etc.
INTERFACE="wlan0"
REPO_DIR="/home/bbb/bbb/"

# Function to check if the network interface is up.
is_interface_up() {
    local iface=$1
    if ip link show "$iface" | grep -q "UP"; then
        return 0
    else
        return 1
    fi
}

# Wait for the network interface to come up.
while ! is_interface_up "$INTERFACE"; do
    echo "Waiting for $INTERFACE to come up..."
    sleep 5
done

# Now that the network is up, change to the directory and execute git pull.
cd "$REPO_DIR" && git pull
# Start the Bridger Bowl Blinker
sudo -u bbb python3 bbb.py &

