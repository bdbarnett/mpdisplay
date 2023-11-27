""" WT32-SC01 Plus 320x480 ST7796 display """
# Usage:
# `from <this file> import display_drv``
# or just use this file as your main.py and add your code.

import mpdisplay
from st7796 import init_sequence, rotations
from backlight import Backlight
from machine import Pin
from time import sleep

# The WT32-SC01 Plus has the reset pins of the display IC and the touch IC both
# tied to pin 4.  Controlling this pin with the display driver can lead to an
# unresponsive touchscreen.  This case is not common.  If they aren't tied 
# together on your board, define reset in mpdisplay.Display instead, like:
#    mpdisplay.Display(reset=4)
# Also do this for the display power pin if your board has one.  Most don't.
reset=Pin(4, Pin.OUT, value=1)

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
    reset=-1,
    rotation=0,
    bgr=True,
    invert_color=True,
    init_sequence=init_sequence,
    rotations=rotations,
)

backlight=Backlight(Pin(45, Pin.OUT), on_high=True)
