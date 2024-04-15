#!/bin/bash

# Installation script for MPDisplay and several libraries that use it.
# After installation, you may use the files in the $TARGET directory to 
# transfer to your MicroPython or CircuitPython device.  You will need
# to replace the board_config.py file with the appropriate file for your
# device and add any drivers it references.

# This script downloads the following repositories:
#   - mpdisplay
#   - displaybuffer
#   - mpconsole
#   - tft_graphics
#   - testris
#   - Adafruit_CircuitPython_Ticks
#   - micropython-touch
#
# It then copies the necessary files to their recommended locations in the
# $TARGET directory and launches the $LAUNCH Python file.
#
# The $REPO and $TARGET directories are created if they do not exist.  The
# $TARGET directory is where the Python files will be copied.  The $BOARD_CONFIG
# variable specifies the board configuration file to use.  The $EXE variable
# specifies the Python executable to use (python3 or micropython).
#
# You may run it as many times as you like from any directory.  The script will
# always copy the files to the $TARGET directory.  If the $TARGET directory
# already exists, the script will overwrite the files in the $TARGET directory.


###################### Set these variables #####################################

#### Set to the executable you want to use for the test at the end of the script
EXE=python3  # micropython, python3 or python

#### Set the following variables to your desired paths
REPO=~/gh  # Path to clone repositories into
TARGET=~/micropython  # Path to copy Python files

##################################################################################


BOARD_CONFIG=mpdisplay/board_configs/desktop/board_config.py
LAUNCH=mpconsole_advanced_demo

# If $REPO directory does not exist, create it
if [ ! -d $REPO ]; then
    mkdir $REPO
fi

# If $TARGET directory does not exist, create it
if [ ! -d $TARGET ]; then
    mkdir $TARGET
fi

##### Clone the repositories.  This will error if the repositories already exist.
git clone https://github.com/bdbarnett/mpdisplay.git $REPO/mpdisplay
git clone https://github.com/bdbarnett/displaybuffer.git $REPO/displaybuffer
git clone https://github.com/bdbarnett/mpconsole.git $REPO/mpconsole
git clone https://github.com/bdbarnett/tft_graphics.git $REPO/tft_graphics
git clone https://github.com/bdbarnett/testris.git $REPO/testris
git clone https://github.com/adafruit/Adafruit_CircuitPython_Ticks.git $REPO/adafruit_circuitpython_ticks
git clone https://github.com/peterhinch/micropython-touch.git $REPO/micropython-touch

# Exit script immediately if any command exits with a non-zero status
set -e

cp -r $REPO/mpdisplay/lib $TARGET/
cp -r $REPO/mpdisplay/examples $TARGET/
cp $REPO/mpdisplay/utils/*.py $TARGET/lib/
cp $REPO/mpdisplay/utils/*.bin $TARGET/
cp $REPO/mpdisplay/utils/lvgl/lv_config.py $TARGET/

cp $REPO/adafruit_circuitpython_ticks/adafruit_ticks.py $TARGET/lib/
cp -r $REPO/displaybuffer/* $TARGET/
cp -r $REPO/mpconsole/* $TARGET/
cp -r $REPO/tft_graphics/* $TARGET/
cp $REPO/testris/testris.py $TARGET/examples/

cp -r $REPO/micropython-touch/gui $TARGET/lib/

rm $TARGET/README.md
rm $TARGET/LICENSE

# if ! test -f $TARGET/board_config.py; then
cp $REPO/$BOARD_CONFIG $TARGET/
# fi

pushd $TARGET
echo
echo "Launching $LAUNCH"
$EXE -i -c "import path, $LAUNCH"
popd
