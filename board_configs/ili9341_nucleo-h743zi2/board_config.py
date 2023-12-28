"""
Adafruit 2.8" TFT Touch Shield for Arduino with Capacitive Touch
on ST Micro STM32 Nucleo-H743ZI2
""" 

from lcd_bus import SPIBus
from ili9341 import ILI9341
from machine import Pin, I2C, SPI
from ft6x36 import FT6x36


display_bus = SPIBus(
    dc='D9',
    cs='D10',
    spi=SPI(1),
    dc_low_on_data=False,
    cs_high_active=False,
)

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
)

i2c = I2C(1, sda=Pin('D14'), scl=Pin('D15'), freq=100000)
touch_drv = FT6x36(i2c)
touch_read_func=touch_drv.get_positions
touch_rotation_table=(6, 3, 0, 5)
