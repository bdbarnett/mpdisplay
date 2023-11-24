""" LilyGo T-HMI 240x320 ST7789 display """
# Usage:
# `from <this file> import display_drv``
# or just use this file as your main.py and add your code.

import mpdisplay
from st7789 import init_sequence, rotations
from backlight import Backlight
from machine import Pin

# Move the following 2 lines to your main.py if
# you need to turn the display off in your code.
display_power_pin=Pin(10, Pin.OUT)
display_power_pin.value(1)

bus = mpdisplay.I80_bus(
    (48, 47, 39, 40, 41, 42, 45, 46),
    dc=7,
    wr=8,
    cs=6,
    swap_color_bytes=True,
    reverse_color_bits=False,
)

display_drv = mpdisplay.Display(
    bus,
    width=240,
    height=320,
    bpp=16,
    reset=-1,
    rotation=0,
    bgr=False,
    invert_color=False,
    init_sequence=init_sequence,
    rotations=rotations,
    backlight=Backlight(Pin(38, Pin.OUT), on_high=True),
)
