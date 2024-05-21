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


palette = display_drv.get_palette()


def deinit(display_drv, display_off=False):
    display_drv.deinit()
    if display_off:
        display_drv.brightness = 0


def config(rotation=None, buffer_size=0, options=0):
    if rotation is not None:
        display_drv.rotation = rotation
    return display_drv
