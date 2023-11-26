""" BPI-Centi-S3 170x320 ST7789 display """
# Usage:
# `from <this file> import display_drv``
# or just use this file as your main.py and add your code.

import mpdisplay
from st7789 import init_sequence, rotations
from backlight import Backlight
from machine import Pin

# If you need to turn the display off in your code, move the following 2 lines to your main.py or use
#   `from <this file> import display_drv, display_power_pin, display_rd_pin`
display_rd_pin = Pin(7, Pin.OUT)
display_rd_pin.value(1)

bus = mpdisplay.I80_bus(
    (8, 9, 10, 11, 12, 13, 14, 15),
    dc=5,
    wr=6,
    cs=4,
    # pclk=16_000_000,
    swap_color_bytes=True,
    reverse_color_bits=False,
    pclk_active_neg=False,
    pclk_idle_low=True,
)

display_drv = mpdisplay.Display(
    bus,
    width=170,
    height=320,
    bpp=16,
    reset=3,
    rotation=0,
    bgr=False,
    invert_color=True,
    init_sequence=init_sequence,
    rotations=rotations,
)

backlight=Backlight(Pin(2, Pin.OUT), on_high=True)
