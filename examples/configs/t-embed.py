""" LilyGo T-embed 170x320 ST7789 display """
# Usage:
# `from <this file> import display_drv``
# or just use this file as your main.py and add your code.

import mpdisplay
from st7789 import init_sequence, rotations
from backlight import Backlight
from machine import Pin

# If you need to turn the display off in your code, move the following 2 lines to your main.py or use
#   `from <this file> import display_drv, display_power_pin, display_rd_pin
display_power_pin=Pin(46, Pin.OUT)
display_power_pin.value(1)

bus = mpdisplay.Spi_bus(
    1,
    mosi=11,
    sck=12,
    dc=13,
    cs=10,
    pclk=60_000_000,
    swap_color_bytes=True,
)

display_drv = mpdisplay.Display(
    bus,
    width=170,
    height=320,
    bpp=16,
    reset=9,
    rotation=0,
    bgr=False,
    invert_color=True,
    init_sequence=init_sequence,
    rotations=rotations,
)

backlight=Backlight(Pin(15, Pin.OUT), on_high=True)
