""" mdisplay_simpletest"""
# Test application for mdisplay drivers
# Currently only works with ESP32 targets, only tested on ESP32S3.
#
# Build your Micropython firmware using directions from:
#     https://github.com/bdbarnett/mpdisplay
#
# Download backlight.py from:
#     https://github.com/bdbarnett/mpdisplay/blob/main/backlight.py
#
# Download the driver for your display:
#     https://github.com/bdbarnett/mpdisplay/tree/main/examples/drivers
#
# Download the config for your board and save it as `display_config`:
#     https://github.com/bdbarnett/mpdisplay/tree/main/examples/configs
#
# If you can't find a driver or config for your board, you will need to
# create your own based on the examples above.  SPI and i80 bus color
# displays are supported.

import random
import mpdisplay
from display_config import display_drv

width = display_drv.width()
height = display_drv.height()
size = 64
num_bufs = 16

# Pre-allocate buffers
buffers = []
for _ in range(num_bufs):
    pixels = size*size
    color = random.randint(0, 65535)  # RGB565 color
    buf = mpdisplay.allocate_buffer(pixels*2)
    for i in range(pixels):
        buf[i*2] = color & 0xff
        buf[i*2+1] = color >> 8
    buffers.append(buf)

# Infinite loop
while True:
    buffer = random.choice(buffers)
    x = random.randint(0, width-size-1)
    y = random.randint(0, height-size-1)
    display_drv.blit(x, y, size, size, buffer)

    
