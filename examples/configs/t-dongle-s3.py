""" LilyGo T-Dongle-S3 80x160 ST7735 display """
# Usage:
# `from <this file> import display_drv``
# or just use this file as your main.py and add your code.

import mpdisplay
from st7735 import init_sequence, rotations
from backlight import Backlight
from machine import Pin

bus = mpdisplay.Spi_bus(
    2,
    mosi=3,
    sck=5,
    dc=2,
    cs=4,
    pclk=50_000_000,
    swap_color_bytes=True
)

display_drv = mpdisplay.Display(
    bus,
    width=80,
    height=160,
    bpp=16,
    reset=1,
    rotation=0,
    bgr=True,
    invert_color=True,
    init_sequence=init_sequence,
    rotations=rotations,
)

backlight=Backlight(Pin(37, Pin.OUT), on_high=False)
