# mpdisplay
C Display Drivers for Micropython including LV_Micropython

Note: this is a work in progress.  It is completely usable now, but the API will likely change.

Supports SPI and i8080 interfaces for many graphics controllers including but not limited to GC9107, GC9A01, ILI9342c, ST7735, ST7789, and ST7796.  For most graphics chips, all that is needed to add them is knowing the chip's init string and rotation modes.

NOTE:  These directions will be updated soon.  This is only a rough draft.  Its intended audience are people who are already familiar with building lv_micropython from source, but possibly not for ESP targets.

Please see the docs/OBJECTIVES.md file for a not so short explanation of the reasoning for creating these drivers.  See docs/TODO.md to see what I have left to do.

mpdisplay is based on s3lcd at https://github.com/russhughes/s3lcd.  Many thanks to Russ Hughes.  s3lcd was modified to create dma buffers to be used by any external graphics library including but not limited to lv_micropthon.  The only useful function exposed to Micropython, other than configuration and housekeeping functions, is `blit`.  All drawing, font, bitmap, png, and file functions have been removed, with the idea those will be provided by the graphics library using these drivers.  Also, the src files have had the ESP32 specific portions moved into separate files, facilitating adding other platform-specific functionality later.  LVGL under Micropython is the test case, but others can work so long as they call this driver's blit function.

mpdisplay currently only supports ESP32 targets, but will likely include STM32, RP2, MIMXRT and non-platform specific in the future.  It has been tested on multiple ESP32S3 boards with multiple types of displays, but should work as-is on any ESP32 microcontroller supported by ESP_LCD in ESP-IDF.

For directions on how to compile Micropython with these drivers, please see docs/COMPILING.md.

Example config and driver files adapted from S3LCD are in the examples folder.

TODO:  Add an mpdisplay_simpletest.py file to test the display without using LVGL.

For an easy way to use these drivers with lv_micropython, please see the example display_driver.py at https://github.com/bdbarnett/lvmp_devices
