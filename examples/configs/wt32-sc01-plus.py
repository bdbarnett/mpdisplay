""" WT32-SC01 Plus 320x480 ST7796 display """
# Usage:
# `from <this file> import display_drv, backlight`
# or just use this file as your main.py and add your code.

import mpdisplay
from st7796 import init_sequence, rotations
from backlight import Backlight
from machine import Pin

bus = mpdisplay.I80_bus(
    (9, 46, 3, 8, 18, 17, 16, 15),
    dc=0,
    wr=47,
    cs=6,
    pclk=20_000_000,
    swap_color_bytes=True,
    reverse_color_bits=False,
)

display_drv = mpdisplay.Display(
    bus,
    width=320,
    height=480,
    bpp=16,
    reset=-1,  # Reset pin 4 is shared with touch.  Should be controlled outside the driver.
    rotation=0,
    bgr=True,
    invert_color=True,
    init_sequence=init_sequence,
    rotations=rotations,
)

backlight=Backlight(Pin(45, Pin.OUT), on_high=True)
