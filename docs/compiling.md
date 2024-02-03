Compiling and testing mp_lcd_bus
--------------------------------
Download and install `esptool.exe` for WSL
==========================================
```
cd ~
wget https://github.com/espressif/esptool/releases/download/v4.7.0/esptool-v4.7.0-win64.zip
unzip esptool-v4.7.0-win64.zip
mkdir bin
mv esptool-win64/esp*.exe bin
rm -rf esptool-win64
rm esptool-v4.7.0-win64.zip
sudo chmod a+x bin/*.exe
```

Download repos and prepare for building
=======================================
```
cd ~
mkdir gh
cd gh
git clone -b v5.0.4 --recursive https://github.com/espressif/esp-idf.git esp-idf-v5.0.4
cd esp-idf-v5.0.4
./install.sh
cd ..
git clone -b v1.22-release --recursive https://github.com/micropython/micropython.git
cd micropython
make -C mpy-cross
cd ..
git clone https://github.com/kdschlosser/
```

Build MicroPython with mp_lcd_bus
=================================
```
pushd ~/gh/esp-idf-v5.0.4 && . export.sh && popd
cd ~/gh/micropython/ports/esp32
make -j BOARD=ESP32_GENERIC_S3 clean
make -j BOARD=ESP32_GENERIC_S3 submodules
make -j BOARD=ESP32_GENERIC_S3 USER_C_MODULES=../../../../mp_lcd_bus/micropython.cmake
```
Change the last 3 lines to compile a board variant
```
make -j BOARD=ESP32_GENERIC_S3 BOARD_VARIANT=SPIRAM clean
make -j BOARD=ESP32_GENERIC_S3 BOARD_VARIANT=SPIRAM submodules
make -j BOARD=ESP32_GENERIC_S3 BOARD_VARIANT=SPIRAM USER_C_MODULES=../../../../mp_lcd_bus/micropython.cmake
```

Flash to your board
===================
<Connect board and put it in bootloader mode>
```
esptool.exe -b 460800 erase_flash
esptool.exe -b 460800 write_flash -z 0x0 build-ESP32_GENERIC_S3-SPIRAM/firmware.bin
```
<Reset your board>

Connect to Wifi and download MPDisplay
======================================
from the REPL
```
import lcd_bus
help(lcd_bus)

import network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
print('Connecting ...')
wlan.connect('SSID', 'PASSWORD')
while not wlan.isconnected(): pass
print('network config:', wlan.ifconfig())

import mip
mip.install("github:bdbarnett/mpdisplay", target="/")
mip.install("github:bdbarnett/mpdisplay/board_configs/YOUR_BOARD_HERE", target="/")

import mpdisplay_simpletest
```