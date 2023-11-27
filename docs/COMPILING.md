# Compiling lv_micropython for ESP32 platform including mpdisplay drivers

These directions are for compiling lv_micropython, but compiling for the base Micropython is very similar.  I plan to create separate directions in the future.  These directions work under Ubuntu on WSL, but can be adapted for your build platform.  See https://github.com/lvgl/lv_micropython for prerequisites.

Install the ESP-IDF.  You need the ESP-IDF for Micropython and these mpdisplay drivers, not for LVGL since the replacement mkrules.cmake file removes the ESP-IDF dependency for lv_binding_micropython.  Currently lv_micropython includes Micropython 1.20, which uses ESP-IDF version 4.x.  Micropython version 1.21 switched to ESP-IDF version 5.x, so your ESP-IDF version will need to be upgraded when lv_micropython is upgraded to Micropython 1.21.  mpdisplay works with ESP-IDF 5.x as well.

We'll call the directory you download the source files to your base directory.

From your base directory:

git clone -b v4.4.6 --recursive https://github.com/espressif/esp-idf.git esp-idf-v4.4.6

cd esp-idf-v4.4.6

./install.sh

. ./export

(Note, to recompile in the future, you will not need to download or install the ESP-IDF again, but you will need to cd into its folder and type the export line above.)

From your base directory:

git clone https://github.com/bdbarnett/mpdisplay.git

git clone --recurse-submodules https://github.com/lvgl/lv_micropython.git

cp mpdisplay/examples/lv_bindings/mkrules.cmake lv_micropython/lib/lv_bindings

cd lv_micropython

make -C mpy-cross

cd ports/esp32

make LV_CFLAGS="-DLV_COLOR_DEPTH=16" BOARD=YOUR_BOARD USER_C_MODULES=../../../../mpdisplay/src/micropython.cmake

The binary to upload to your board is in your base directory at lv_micropython/ports/esp32/build-YOUR_BOARD/firmware.bin.  There are many ways to upload it to your board, including esptool and Thonny.  Please look for a solution you like online.
