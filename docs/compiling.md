Compiling and testing MicroPython & mp_lcd_bus with WSL
=======================================================
The following is my method of compiling and testing MPDisplay with [mp_lcd_bus](https://github.com/kdschlosser/mp_lcd_bus) for ESP32-S3 boards.  I use Ubuntu under Windows Subsystem for Linux (WSL).  Your method will be different if you have a different build environment.  This is not a full tutorial.  I documented it for my own reference and decided to post it online in case it my be useful to someone else.  See the official directions on the [MicroPython repository](https://github.com/micropython/micropython/tree/master/ports/esp32).  There are several Linux packages that will need to be installed beforehand using `sudo apt install`.  

Download and install `esptool.exe` for use in WSL (once only)
-------------------------------------------------------------
I use ESPTool to flash firmware to ESP32 boards.  It is written in Python and is available as `esptool.py` for any OS with Python installed and as `esptool.exe` for Windows.  `esptool.py` searches for the serial port in the normal Unix places under /dev.  WSL doesn't forward COM ports to /dev (at least by default), so it is easier to use `esptool.exe`, which searches for COM ports.  Fortunately, Windows EXE files can be run from inside the WSL shell so long as the full filename including .exe is used.

At the bash prompt:
```
cd ~                           # Change to the current user's home directory

# This will error out if "bin" already exists.  If it doesn't you will likely
# need to restart the shell for it to be added to your system path.
mkdir bin

# Download and unzip ESPTool for Windows
wget https://github.com/espressif/esptool/releases/download/v4.7.0/esptool-v4.7.0-win64.zip
unzip esptool-v4.7.0-win64.zip

mv esptool-win64/esp*.exe bin  # Move the unzipped .exe files to the bin folder
rm -rf esptool-win64           # Delete the folder created with unzip
rm esptool-v4.7.0-win64.zip    # Delete the downloaded .zip file
sudo chmod a+x bin/*.exe       # Make the new .exe files executable
```

Download repos and prepare for building (once only)
---------------------------------------------------
At the bash prompt:
```
# I put all Github repositories in the "gh" directory.  Use your preferred directory.
cd ~
mkdir gh
cd gh

# Download and install the recommended version of Espressif ESP-IDF
git clone -b v5.0.4 --recursive https://github.com/espressif/esp-idf.git esp-idf-v5.0.4
cd esp-idf-v5.0.4
./install.sh
cd ..

# Download MicroPython and build the MPY cross compiler
git clone -b v1.22-release --recursive https://github.com/micropython/micropython.git
cd micropython
make -C mpy-cross
cd ..

# Download mp_lcd_bus
git clone https://github.com/kdschlosser/
```

Build MicroPython with mp_lcd_bus
---------------------------------
Begin here for future builds and rebuilds.  This first line is only needed once per login session.  I save it as a bash alias `esp5` so I can easily run it from any directory.

At the bash prompt:
```
pushd ~/gh/esp-idf-v5.0.4 && . export.sh && popd
```
To build the **base** ESP32_GENERIC_S3 variant:
```
cd ~/gh/micropython/ports/esp32
make -j BOARD=ESP32_GENERIC_S3 clean
make -j BOARD=ESP32_GENERIC_S3 submodules
make -j BOARD=ESP32_GENERIC_S3 USER_C_MODULES=../../../../../ext_mod/lcd_bus/micropython.cmake
```
To build the **SPIRAM** ESP32_GENERIC_S3 variant:
```
cd ~/gh/micropython/ports/esp32
make -j BOARD=ESP32_GENERIC_S3 BOARD_VARIANT=SPIRAM clean
make -j BOARD=ESP32_GENERIC_S3 BOARD_VARIANT=SPIRAM submodules
make -j BOARD=ESP32_GENERIC_S3 BOARD_VARIANT=SPIRAM USER_C_MODULES=../../../../../ext_mod/lcd_bus/micropython.cmake
```
To build the **SPIRAM_OCT** ESP32_GENERIC_S3 variant:
```
cd ~/gh/micropython/ports/esp32
make -j BOARD=ESP32_GENERIC_S3 BOARD_VARIANT=SPIRAM_OCT clean
make -j BOARD=ESP32_GENERIC_S3 BOARD_VARIANT=SPIRAM_OCT submodules
make -j BOARD=ESP32_GENERIC_S3 BOARD_VARIANT=SPIRAM_OCT USER_C_MODULES=../../../../../ext_mod/lcd_bus/micropython.cmake
```

Flash the firmware to your board
--------------------------------
Connect the board and put it in bootloader mode, usually by holding the boot button while pressing the reset button.  Note the number after `-b` is the baudrate.  Some computers can go faster, but my main build machine is limited to this speed, so I stick with it.  YMMV.  Also note, we aren't specifying which COM port the board is on, so ESPTool uses the first one it finds.  If you use these commands, be sure there are no other serial devices connected!

At the bash prompt:
```
# Note we are still in the ~/gh/micropython/ports/esp32 directory
esptool.exe erase_flash
esptool.exe -b 460800 write_flash -z 0x0 build-ESP32_GENERIC_S3-SPIRAM/firmware.bin
```
Reset your board

Connect to your board to wifi and download MPDisplay
----------------------------------------------------
There are many ways to get to the REPL, including `mpremote`, PuTTY and Thonny.  Use your preferred method.

At the REPL:
```
import lcd_bus    # Just to confirm it compiled in correctly

import network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
print('Connecting ...')
wlan.connect('SSID', 'PASSWORD')            ## Change to your SSID and PASSWORD ##
while not wlan.isconnected(): pass
print('network config:', wlan.ifconfig())

import mip
mip.install("github:bdbarnett/mpdisplay", target="/") ## Change YOUR_BOARD_HERE ##
mip.install("github:bdbarnett/mpdisplay/board_configs/YOUR_BOARD_HERE", target="/")

import mpdisplay_simpletest
```
https://stackoverflow.com/questions/29306032/fork-subdirectory-of-repo-as-a-different-repo-in-github
