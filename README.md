# mpdisplay
C Display Drivers for Micropython including LV_Micropython

Note: this is a work in progress.  It is completely usable now, but the API will likely change.

Supports SPI and i8080 interfaces for many graphics controllers including but not limited to GC9107, GC9A01, ILI9342c, ST7735, ST7789, and ST7796.  For most graphics chips, all that is needed to add them is knowing the chips init string and rotation modes.  There will be many examples in the examples/config folder soon as I find them.

NOTE:  These directions will be updated soon.  This is only a rough draft and its intended audience is people who are already familiar with building lv_micropython from source, but possibly not for ESP targets.

Please see the OBJECTIVES.md file for a not so short explanation of the reasoning for creating these drivers.

mpdisplay is based on s3lcd at https://github.com/russhughes/s3lcd.  Many thanks to Russ Hughes.  s3lcd was modified to create dma buffers to be used by any external graphics library including but not limited to lv_micropthon.  The only useful function exposed to Micropython, other than configuration and housekeeping functions, is `blit`.  All drawing, font, bitmap, png, and file functions have been removed, with the idea those will be provided by the graphics library using these drivers.  Also, the src files have had the ESP32 specific portions moved into separate files, facilitating adding other platform-specific files later.  LVGL under Micropython is the test case, but others can work so long as they call this driver's blit function.  The drivers are instantiated the same way as s3lcd, but the following arguments have been removed since they are not needed:  color_space, dma_rows, options.  Also, s3lcd drivers require calling init after the display object is created, whereas mpdisplay calls init internally, so there is no need to call init.  The init function is still exposed to Micropython in case it might be useful after a deinit for some reason, but that exposure is likely to be removed in the future.

mpdisplay currently only supports ESP32 targets, but will likely include STM32 and RP2 in the future, and maybe others.  They have been tested on multiple ESP32S3 boards with multiple types of displays.

To use these driver with LVGL for Micropython:
(These directions work under WSL, but can be adapted for your situation.)

We'll call the directory you download the source files to your base directory.

Install the ESP-IDF.  You'll need the ESP-IDF for Micropython and these mpdisplay drivers, not for LVGL.  Currently lv_micropython includes Micropython 1.20, which uses ESP-IDF version 4.x.  Micropython version 1.21 switched to ESP-IDF version 5.x, so your ESP-IDF version will need to be upgraded when lv_micropython is upgraded to Micropython 1.21.  mpdisplay works with ESP-IDF 5.x as well.

From your base directory:
git clone -b v4.4.6 --recursive https://github.com/espressif/esp-idf.git esp-idf-v4.4.6
cd esp-idf-v4.4.6
./install.sh
. ./export

(Note, to recompile in the future, you will not need to download or install the ESP-IDF again, but you will need to cd into its folder and type the export line above.)

From your base directory
git clone https://github.com/bdbarnett/mpdisplay.git
git clone --recurse-submodules https://github.com/lvgl/lv_micropython.git
(edit or replace the mkrules.cmake in lv_micropython/lib/lv_bindings as explained in examples/lv_bindings)
cp mpdisplay/examples/lv_bindings/mkrules.cmake lv_micropython/lib/lv_bindings
cd lv_micropython
make -C mpy-cross
cd ports/esp32
make -C LV_CFLAGS="-DLV_COLOR_DEPTH=16" BOARD=YOUR_BOARD USER_C_MODULES=../../../../mpdisplay/src/micropython.cmake

The binary to upload to your board is in your base directory at lv_micropython/ports/esp32/build-YOUR_BOARD/firmware.bin.  There are many ways to upload it to your board, including esptool and Thonny.  Please look for a solution you like online.

In the coming days, I will create example configuration files and put them in the examples/configs folder here.  For now, download config files from
https://github.com/russhughes/s3lcd/tree/main/examples/configs
You will need to change all references to s3lcd to mpdisplay, change SPI_BUS to Spi_bus or I80_BUS to I80_bus to match Python naming conventions for classes, change ESPLCD to Display, and remove the color_space, dma_rows and options parameters, as they are not used by mpdisplay.  Also, s3lcd drivers require calling .init() after the display object has been created, whereas the display object is already inited in mpdisplay objects and should not be called again.  Finally, add add display_drv = config() to the bottom of the file.  Then you can create the display object like:

from tft_config import display_drv

Don't worry, I'll make this simpler and have better examples in the near future.

TODO:  Add info about creating buffers and lv.disp_create() or lv.display_create()
