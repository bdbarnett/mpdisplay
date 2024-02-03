Compiling and testing mp_lcd_bus
================================
The following is my method of compiling and testing MPDisplay with [mp_lcd_bus](https://github.com/kdschlosser/mp_lcd_bus) for ESP32-S3 boards.  I use Windows Subsystem for Linux (WSL).  Your method will be different if you have a different build environment.

Download and install `esptool.exe` for use in WSL (once only)
-------------------------------------------------------------
I use ESPTool to flash firmware to ESP32 boards.  It is written in Python and is available as `esptool.py` for any OS with Python installed and as `esptool.exe` for Windows.  `esptool.py` searches for the serial port in the normal Unix places under /dev.  WSL doesn't forward COM ports to /dev (at least by default), so it is easier to use `esptool.exe`, which searches for COM ports.  Fortunately, Windows EXE files can be run from inside the WSL shell so long as the full filename including .EXE is used.

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

# Download MicroPython and build the MPY cross compiler
cd ..
git clone -b v1.22-release --recursive https://github.com/micropython/micropython.git
cd micropython
make -C mpy-cross

# Download mp_lcd_bus
cd ..
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
make -j BOARD=ESP32_GENERIC_S3 USER_C_MODULES=../../../../mp_lcd_bus/micropython.cmake
```
To build the **SPIRAM** ESP32_GENERIC_S3 variant:
```
cd ~/gh/micropython/ports/esp32
make -j BOARD=ESP32_GENERIC_S3 BOARD_VARIANT=SPIRAM clean
make -j BOARD=ESP32_GENERIC_S3 BOARD_VARIANT=SPIRAM submodules
make -j BOARD=ESP32_GENERIC_S3 BOARD_VARIANT=SPIRAM USER_C_MODULES=../../../../mp_lcd_bus/micropython.cmake
```
To build the **SPIRAM_OCT** ESP32_GENERIC_S3 variant:
```
make -j BOARD=ESP32_GENERIC_S3 BOARD_VARIANT=SPIRAM_OCT clean
make -j BOARD=ESP32_GENERIC_S3 BOARD_VARIANT=SPIRAM_OCT submodules
make -j BOARD=ESP32_GENERIC_S3 BOARD_VARIANT=SPIRAM_OCT USER_C_MODULES=../../../../mp_lcd_bus/micropython.cmake
```

Flash the firmware to your board
--------------------------------
Connect the board and put it in bootloader mode, usually by holding the boot button while pressing the reset button.

At the bash prompt:
```
esptool.exe -erase_flash
esptool.exe -b 460800 write_flash -z 0x0 build-ESP32_GENERIC_S3-SPIRAM/firmware.bin
```
Reset your board

Connect to your board to wifi and download MPDisplay
----------------------------------------------------
At the REPL:
```
import lcd_bus    # Just to confirm it is built-in

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
