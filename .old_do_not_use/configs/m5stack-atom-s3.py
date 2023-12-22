""" M5STACK ATOM-S3 N085-1212TBWIG06-C08 128x128 display """
# Usage:
# `from <this file> import display_drv``
# or just use this file as your main.py and add your code.

import mpdisplay
from n085_1212tbwig06_c08 import init_sequence, rotations
from backlight import Backlight
from machine import Pin

bus = mpdisplay.Spi_bus(
    2,
    mosi=21,
    sck=17,
    dc=33,
    cs=15,
    pclk=27_000_000,
)

display_drv = mpdisplay.Display(
    bus,
    width=128,
    height=128,
    bpp=16,
    reset=34,
    rotation=0,
    bgr=True,
    invert_color=True,
    init_sequence=init_sequence,
    rotations=rotations,
)

backlight=Backlight(Pin(16, Pin.OUT), on_high=True)
