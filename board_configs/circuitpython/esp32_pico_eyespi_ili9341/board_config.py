""" QTPy ESP32 Pico with EyeSPI and ILI9341 2.8" display """

import board
from fourwire import FourWire
from ili9341 import ILI9341
from adafruit_focaltouch import Adafruit_FocalTouch

import displayio
displayio.release_displays()

display_bus = FourWire(
    board.SPI(),
    command=board.RX,
    chip_select=board.TX,
#     reset=None,
#     baudrate=24000000,
#     polarity=0,
#     phase=0,
)

i2c = board.I2C()
touch_drv = Adafruit_FocalTouch(i2c)

def touch_point():
    touches = touch_drv.touches
    if len(touches):
        return touches[0]['x'], touches[0]['y']

display_drv = ILI9341(
    display_bus,
    width=240,
    height=320,
    colstart=0,
    rowstart=0,
    rotation=0,
    mirrored=False,
    color_depth=16,
    bgr=True,
    reverse_bytes_in_word=True,
    invert=False,
    brightness=1.0,
    backlight_pin=None,
    backlight_on_high=True,
    reset_pin=None,
    reset_high=True,
    power_pin=None,
    power_on_high=True,
    touch_read_func=touch_point,
    touch_rotation_table=(6, 3, 0, 5),
)
