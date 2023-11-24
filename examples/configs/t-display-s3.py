""" LilyGo T-DISPLAY-S3 170x320 ST7789 display """
# Usage:
# `from <this file> import display_drv``
# or just use this file as your main.py and add your code.

import mpdisplay
from st7789 import init_sequence, rotations
from backlight import Backlight
from machine import Pin

# If you need to turn the display off in your code, move the following 4 lines to your main.py or use
#   `from <this file> import display_drv, display_power_pin, display_rd_pin`
display_power_pin=Pin(15, Pin.OUT)
display_power_pin.value(1)
display_rd_pin = Pin(9, Pin.OUT)
display_rd_pin.value(1)

bus = mpdisplay.I80_bus(
    (39, 40, 41, 42, 45, 46, 47, 48),
    dc=7,
    wr=8,
    cs=6,
    pclk=20_000_000,
    swap_color_bytes=True,
    reverse_color_bits=False,
)

display_drv = mpdisplay.Display(
    bus,
    width=170,
    height=320,
    bpp=16,
    reset=5,
    rotation=0,
    bgr=False,
    invert_color=True,
    init_sequence=init_sequence,
    rotations=rotations,
    backlight=Backlight(Pin(38, Pin.OUT), on_high=True)
)
