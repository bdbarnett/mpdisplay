#!/bin/bash

# Installation script for MPDisplay and several libraries that use it.
#
# Prerequisites:  The only prerequisites to use this script to download and stage
# the files is git, which is preinstalled on nearly all Linux distros, including WSL.
#
# To use MPDisplay in desktop operating systems, you will need either SDL2 or PyGame.
# Here is how you get them on Ubuntu under WSL:
#
#     sudo apt update  && sudo apt upgrade
#     sudo apt install libsdl2-2.0-0
#                   OR
#     sudo apt install python3-pygame
#
# Python3 is installed on nearly all Linux Distros.  If your distro has a package
# for MicroPython, like Ubuntu does on WSL, you may get it with:
#
#     sudo apt install micropython
#
# After downloading, cd to the directory your files are staged in and launch *Python.
# For instance:
#
#     cd ~/mp
#     micropython -i path.py
#             OR
#     python3 -i path.py
#
# You may then import any of the examples, such as 'import paint'
#
# Usage:
#     wget https://raw.githubusercontent.com/bdbarnett/mpdisplay/main/installers/mpd_install.sh
#     (edit mpd_install.sh to set the $REPO, $TARGET and $EXE variables below)
#     chmod u+x install.sh
#     ./mpd_install.sh
#
# After installation, you may use the files in the $TARGET directory to 
# transfer to your MicroPython or CircuitPython device.  You will need
# to replace the board_config.py file with the appropriate file for your
# device and add any drivers it references.
#
# This script clones the following repositories into the $REPO directory:
# - mpdisplay
# - lcd_bus
# - console
# - timer
# - playing_cards
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
#
#     python3 -i path.py
# or
#     micropython -i path.py
#
# That will add the directories necessary to run the demos to the path and leave
# you at the REPL.  Or, type the following ommitting the '.py' file extensions:
#
#     python3 -c "import path, <EXAMPLE>"
# or
#     micropython -c "import path, <EXAMPLE>"
#
# Remember:
#     - All examples other than those for LVGL should run on MicroPython on Unix.
#     - Examples that use MicroPython specific libraries, such as those based on
#       the MicroPython-Touch library in the gui directory will not run on
#       CPython.
#     - While MPDisplay suppots LVGL on microntrollers, it doesn't support LVGL
#       on desktop operating systems, including MicroPython on Unix.


##################### Required: set these variables #####################################

#### Set the following variables to your desired paths
REPO=~/gh  # Path to clone repositories into
TARGET=~/mp  # Path to copy Python files

#### Set to the executable you want to use for the test at the end of the script
EXE=python3  # micropython, python3 or python


##################### Optional: set these variables #####################################

BOARD_CONFIG=mpdisplay/board_configs/desktop/board_config.py  # with .py extension
LAUNCH=paint  # without .py extension


######################## Download the repositories ###############################

# If $REPO directory does not exist, create it
if [ ! -d $REPO ]; then
    mkdir $REPO
fi

##### Clone the repositories.  This will error if the repositories already exist.
git clone https://github.com/bdbarnett/mpdisplay.git $REPO/mpdisplay
git clone https://github.com/bdbarnett/lcd_bus.git $REPO/lcd_bus
git clone https://github.com/bdbarnett/timer.git $REPO/timer
git clone https://github.com/bdbarnett/console.git $REPO/console
git clone https://github.com/bdbarnett/playing_cards.git $REPO/playing_cards
git clone https://github.com/bdbarnett/testris.git $REPO/testris
git clone https://github.com/peterhinch/micropython-touch.git $REPO/micropython-touch


######################## Create the directory structure ##############################

# Exit script immediately if any command exits with a non-zero status
set -e

# If $TARGET directory does not exist, create it
if [ ! -d $TARGET ]; then
    mkdir $TARGET
fi

######################## Stage the files in $TARGET ##############################

cp -u $REPO/$BOARD_CONFIG $TARGET/

cp -ur $REPO/mpdisplay/lib $TARGET/
cp -ur $REPO/mpdisplay/fonts $TARGET/
cp -ur $REPO/mpdisplay/examples $TARGET/
cp -ur $REPO/mpdisplay/utils/* $TARGET/lib/
cp -u $REPO/mpdisplay/configs/* $TARGET/

cp -ur $REPO/lcd_bus/lcd_bus $TARGET/lib/

cp -ur $REPO/timer/timer $TARGET/lib/
cp -ur $REPO/timer/examples $TARGET/

cp -u $REPO/console/console.py $TARGET/lib/
cp -ur $REPO/console/examples $TARGET/

cp -u $REPO/playing_cards/playing_cards.py $TARGET/lib/
cp -ur $REPO/playing_cards/examples $TARGET/

cp -u $REPO/testris/testris.py $TARGET/examples/

cp -ur $REPO/micropython-touch/gui $TARGET/


######################## Launch the test app ####################################

echo
echo "Installation complete.  To run the '$LAUNCH' example, type the following:"
echo
echo "cd $TARGET"
echo "$EXE -i path.py"
echo "import $LAUNCH"
echo

