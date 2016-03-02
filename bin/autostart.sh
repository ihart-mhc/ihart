#!/bin/sh

# Run this file as ./autostart.sh on Unix, or sh ./autostart.sh on Windows.
# If you want to change what this file does, change the variables in autostart.config.

# Get where we are.
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

# Load configuration file.
source "$DIR/autostart.config"

# Directory where the server file is located. This is mac for OS X, windows for Windows.
# Which server file to run. On Windows, make sure to include the .exe extension.

if $OS_OSX
then
	SERVERDIR="$DIR/../server/dist/mac/"
	SERVERFILE="cvServer-2.3"
else
	SERVERDIR="$DIR/../server/dist/windows/"
	SERVERFILE="cvServer-2.3.exe"
fi



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

if $OS_OSX
then
	open $APP &
else
	./$APP &
fi

if $OS_OSX
then
	/usr/bin/osascript -e 'tell application "Flash Player"' -e "activate" -e 'tell application "System Events"' -e 'keystroke "f" using {command down}' -e "end tell" -e "end tell"
fi
