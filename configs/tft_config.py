from board_config import display_drv
from sys import implementation

if implementation.name == "esp32":
    from machine import freq

    freq(240_000_000)


TFA = 0
BFA = 0

if display_drv.height > display_drv.width:
    TALL = display_drv.rotation
    WIDE = display_drv.rotation + 90
else:
    WIDE = display_drv.rotation
    TALL = display_drv.rotation + 90

SCROLL = WIDE  # orientation for scroll.py
FEATHERS = TALL  # orientation for feathers.py


class Palette:
    color565 = display_drv.color565

    BLACK = color565(0, 0, 0)
    RED = color565(255, 0, 0)
    GREEN = color565(0, 255, 0)
    BLUE = color565(0, 0, 255)
    CYAN = color565(0, 255, 255)
    MAGENTA = color565(255, 0, 255)
    YELLOW = color565(255, 255, 0)
    WHITE = color565(255, 255, 255)


def deinit(tft, display_off=False):
    tft.deinit()
    if display_off:
        BL.value(0)


def config(rotation=None, buffer_size=0, options=0):
    if rotation is not None:
        display_drv.rotation = rotation
    return display_drv
