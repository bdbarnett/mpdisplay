#!/bin/bash

# Installation script for MPDisplay and several libraries that use it.
#
# Usage:
#     wget https://raw.githubusercontent.com/bdbarnett/mpdisplay/main/install.sh
#     chmod u+x install.sh
#     (edit install.sh to set the $REPO, $TARGET and $EXE variables below)
#     ./install.sh
#
# After installation, you may use the files in the $TARGET directory to 
# transfer to your MicroPython or CircuitPython device.  You will need
# to replace the board_config.py file with the appropriate file for your
# device and add any drivers it references.
#
# This script clones the following repositories into the $REPO directory:
# - mpdisplay
# - sdl2_lib
# - lcd_bus
# - displaybuf
# - console
# - tft_graphics
# - timer
# - framebuf
# - binfont
# - testris
# - micropython-touch
#
# It then copies the necessary files to their recommended locations in the
# $TARGET directory and launches the $LAUNCH Python file as a test.  The $REPO
# and $TARGET directories are created if they do not exist.  The $EXE variable
# specifies the Python executable to use (python3 or micropython).
#
# You may run the script as many times as you like from any directory.  After 
# runnng the first time, it will print an error for each repository it tries to
# download since they are already downloaded, but that can be ignored.  (Note,
# if you want to update a repo, 'cd' into its directory and type 'git pull'.)
# All files will be copied from $REPO to $TARGET each time it is run, regardless
# of whether the files in $TARGET have changed, so be careful not to overwrite
# your changes.  It is recommended to make your changes in the $REPO directory
# and then run this script to copy them to $TARGET for testing and transer to
# a microcontroller.
#
# For testing purposes, it is recommended you 'cd' into the directory specified
# by $TARGET and type either
#     python3 -i path.py
# or
#     micropython -i path.py
# That will add the directories necessary to run the demos to the path and leave
# you at the REPL.  Or, type the following ommitting the '.py' file extensions:
#     python3 -c "import path, <EXAMPLE>"
# or
#     micropython -c "import path, <EXAMPLE>"
#
# Remember:
#     - All examples other than those for LVGL should run on MicroPython on Unix.
#     - Examples that use MicroPython specific libraries, such as those based on
#       the MicroPython-Touch library in the lib/gui directory will not run on
#       CPython.
#     - While MPDisplay suppots LVGL on microntrollers, it doesn't support LVGL
#       on desktops operating systems, including MicroPython on Unix.


##################### Required: set these variables #####################################

#### Set the following variables to your desired paths
REPO=~/gh  # Path to clone repositories into
TARGET=~/micropython  # Path to copy Python files

#### Set to the executable you want to use for the test at the end of the script
EXE=python3  # micropython, python3 or python


##################### Optional: set these variables #####################################

BOARD_CONFIG=mpdisplay/board_configs/desktop/board_config.py  # with .py extension
#LAUNCH=mpdisplay_paint  # without .py extension
LAUNCH=paint  # without .py extension


######################## Download the repositories ###############################

# If $REPO directory does not exist, create it
if [ ! -d $REPO ]; then
    mkdir $REPO
fi

##### Clone the repositories.  This will error if the repositories already exist.
git clone https://github.com/bdbarnett/mpdisplay.git $REPO/mpdisplay
git clone https://github.com/bdbarnett/sdl2_lib.git $REPO/sdl2_lib
git clone https://github.com/bdbarnett/lcd_bus.git $REPO/lcd_bus
git clone https://github.com/bdbarnett/displaybuf.git $REPO/displaybuf
git clone https://github.com/bdbarnett/console.git $REPO/console
git clone https://github.com/bdbarnett/tft_graphics.git $REPO/tft_graphics
git clone https://github.com/bdbarnett/timer.git $REPO/timer
git clone https://github.com/bdbarnett/framebuf.git $REPO/framebuf
git clone https://github.com/bdbarnett/binfont.git $REPO/binfont
git clone https://github.com/bdbarnett/testris.git $REPO/testris
git clone https://github.com/peterhinch/micropython-touch.git $REPO/micropython-touch


######################## Create the directory structure ##############################

# Exit script immediately if any command exits with a non-zero status
set -e

# If $TARGET directory does not exist, create it
if [ ! -d $TARGET ]; then
    mkdir $TARGET
fi

# If $TARGET/lib directory does not exist, create it
if [ ! -d $TARGET/lib ]; then
    mkdir $TARGET/lib
fi

# If $TARGET/examples directory does not exist, create it
if [ ! -d $TARGET/examples ]; then
    mkdir $TARGET/examples
fi

######################## Stage the files in $TARGET ##############################

cp -u $REPO/$BOARD_CONFIG $TARGET/

cp -ur $REPO/mpdisplay/mpdisplay $TARGET/lib/
cp -ur $REPO/mpdisplay/examples $TARGET/
cp -u $REPO/mpdisplay/utils/* $TARGET/lib/
cp -u $REPO/mpdisplay/configs/* $TARGET/
cp -u $REPO/mpdisplay/install.py $TARGET/

cp -ur $REPO/sdl2_lib/sdl2_lib $TARGET/lib/

cp -ur $REPO/lcd_bus/lcd_bus $TARGET/lib/

cp -u $REPO/framebuf/framebuf.py $TARGET/lib/
cp -ur $REPO/framebuf/examples $TARGET/

cp -u $REPO/binfont/binfont.py $TARGET/lib/
cp -ur $REPO/binfont/examples $TARGET/
cp -ur $REPO/binfont/romfonts $TARGET/

cp -ur $REPO/displaybuf/displaybuf $TARGET/lib/
cp -ur $REPO/displaybuf/examples $TARGET/
cp -u $REPO/displaybuf/configs/* $TARGET/

cp -ur $REPO/tft_graphics/tft_graphics $TARGET/lib/
cp -ur $REPO/tft_graphics/examples $TARGET/
cp -ur $REPO/tft_graphics/romfonts $TARGET/

cp -u $REPO/console/console.py $TARGET/lib/
cp -ur $REPO/console/examples $TARGET/

cp -ur $REPO/timer/timer $TARGET/lib/
cp -ur $REPO/timer/examples $TARGET/

cp -u $REPO/testris/testris.py $TARGET/examples/

cp -ur $REPO/micropython-touch/gui $TARGET/lib/


######################## Launch the test app ####################################

pushd $TARGET
echo
echo "Launching $LAUNCH"
echo
$EXE -c "import path, $LAUNCH"
popd
