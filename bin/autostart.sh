#!/bin/sh

# Run this file as ./autostart.sh on Unix, or sh ./autostart.sh on Windows.
# If you want to change what this file does, change the variables in autostart.config.

# Load configuration file.
source "./autostart.config"

# Run the server in the background.
SERVER="$SERVERDIR$SERVERFILE"
./$SERVER --autostart &

# Exit if the server failed to run.
case $? in
    0 ) break;;
    * ) echo "Server did not start successfully! Exiting."; exit 1;;
esac

# Wait for server to load and access camera before running the app,
# to make sure the server starts sending info first.
sleep 5


# Run the application in the background.
APP="$APPDIR$APPFILE"
./$APP &